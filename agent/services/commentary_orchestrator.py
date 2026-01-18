from typing import Optional, Dict, Any
import logging
from services.frame_window_service import FrameWindowService
from services.gemini_vision import GeminiVisionAnalyzer
from services.commentary_deduplicator import CommentaryDeduplicator

logger = logging.getLogger(__name__)


class CommentaryOrchestrator:
    
    def __init__(self):
        self.frame_service = FrameWindowService()
        self.vision_analyzer = GeminiVisionAnalyzer()
        self.deduplicators: Dict[str, CommentaryDeduplicator] = {}
    
    async def generate_live_commentary(
        self,
        video_url: str,
        current_time: float,
        window_size: float = 5.0
    ) -> Dict[str, Any]:
        try:
            video_id = self._get_video_id(video_url)
            if video_id not in self.deduplicators:
                self.deduplicators[video_id] = CommentaryDeduplicator()
            
            deduplicator = self.deduplicators[video_id]
            
            logger.info(f"[ORCHESTRATOR] Generating commentary for {video_url} at {current_time:.1f}s")
            
            logger.info("[ORCHESTRATOR] Extracting frame window for Gemini Vision...")
            frames, timestamps = await self.frame_service.get_frame_window(
                video_url,
                current_time,
                window_size=window_size
            )
            
            if not frames:
                logger.warning("[ORCHESTRATOR] No frames extracted - returning stub")
                return {
                    "commentary": None,
                    "raw_action": None,
                    "timestamp": current_time,
                    "skipped": False,
                    "error": "No frames extracted"
                }
            
            logger.info(f"[ORCHESTRATOR] ✓ Extracted {len(frames)} frames")
            
            logger.info("[ORCHESTRATOR] Analyzing with Gemini Vision...")
            commentary = await self.vision_analyzer.analyze_frame_window(frames, timestamps)

            if not commentary or len(commentary.strip()) < 5:
                raise RuntimeError("Gemini Vision returned empty/invalid commentary")

            logger.info(f"[ORCHESTRATOR] ✓ Commentary: {commentary[:80]}...")
            
            logger.info("[ORCHESTRATOR] Checking deduplication...")
            should_skip = deduplicator.should_skip(commentary)
            
            if should_skip:
                logger.info("[ORCHESTRATOR] ✗ Commentary skipped (too similar to recent)")
                return {
                    "commentary": None,
                    "raw_action": commentary,
                    "timestamp": current_time,
                    "skipped": True
                }
            
            deduplicator.add_commentary(commentary, current_time)
            
            logger.info("[ORCHESTRATOR] ✓ Commentary accepted and added to history")
            
            return {
                "commentary": commentary,
                "raw_action": commentary,
                "timestamp": current_time,
                "skipped": False
            }
            
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Error in pipeline: {e}")
            import traceback
            traceback.print_exc()
            return {
                "commentary": None,
                "raw_action": None,
                "timestamp": current_time,
                "skipped": False,
                "error": str(e)
            }
    
    def _get_video_id(self, video_url: str) -> str:
        if "youtube.com/watch?v=" in video_url or "youtu.be/" in video_url:
            if "youtube.com/watch?v=" in video_url:
                return video_url.split("youtube.com/watch?v=")[1].split("&")[0].split("?")[0]
            elif "youtu.be/" in video_url:
                return video_url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        return video_url
    
    def clear_history(self, video_url: Optional[str] = None):
        if video_url:
            video_id = self._get_video_id(video_url)
            if video_id in self.deduplicators:
                self.deduplicators[video_id].clear_history()
                logger.info(f"[ORCHESTRATOR] History cleared for {video_id}")
        else:
            for video_id in self.deduplicators:
                self.deduplicators[video_id].clear_history()
            logger.info("[ORCHESTRATOR] All history cleared")