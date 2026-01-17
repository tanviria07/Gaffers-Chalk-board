from typing import Optional, Dict, Any
import logging
from services.frame_window_service import FrameWindowService
from services.gemini_vision import GeminiVisionAnalyzer
from services.gemini_commentary import GeminiCommentaryEnhancer
from services.commentary_deduplicator import CommentaryDeduplicator

logger = logging.getLogger(__name__)


class CommentaryOrchestrator:
    
    def __init__(self):
        self.frame_service = FrameWindowService()
        self.vision_analyzer = GeminiVisionAnalyzer()
        self.commentary_enhancer = GeminiCommentaryEnhancer()
        self.deduplicator = CommentaryDeduplicator()
    
    async def generate_live_commentary(
        self,
        video_url: str,
        current_time: float,
        window_size: float = 5.0
    ) -> Dict[str, Any]:
        try:
            logger.info(f"[ORCHESTRATOR] Generating commentary for {video_url} at {current_time:.1f}s")
            
            raw_action = None
            
            import os
            if os.getenv("OVERSHOOT_API_KEY"):
                try:
                    logger.info("[ORCHESTRATOR] Step 1: Trying Overshoot...")
                    import httpx
                    overshoot_url = os.getenv("OVERSHOOT_SERVICE_URL", "http://localhost:3002")
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{overshoot_url}/get-frame-window",
                            json={
                                "videoUrl": video_url,
                                "currentTime": current_time,
                                "windowSize": window_size
                            }
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success") and data.get("commentary"):
                                raw_action = data.get("commentary") or data.get("rawAction")
                                logger.info(f"[ORCHESTRATOR] ✓ Got raw action from Overshoot: {raw_action[:50]}...")
                except Exception as e:
                    logger.warning(f"[ORCHESTRATOR] Overshoot failed: {e}, falling back to Gemini Vision")
            
            if not raw_action:
                logger.info("[ORCHESTRATOR] Step 2: Extracting frame window for Gemini Vision...")
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
                
                logger.info("[ORCHESTRATOR] Step 2b: Analyzing with Gemini Vision...")
                raw_action = await self.vision_analyzer.analyze_frame_window(frames, timestamps)
                logger.info(f"[ORCHESTRATOR] ✓ Raw action: {raw_action[:50]}...")
            
            logger.info("[ORCHESTRATOR] Step 3: Enhancing with Gemini Text...")
            enhanced_commentary = await self.commentary_enhancer.enhance_commentary(
                raw_action,
                style="Broadcast",
                detail_level="Normal"
            )
            logger.info(f"[ORCHESTRATOR] ✓ Enhanced commentary: {enhanced_commentary[:50]}...")
            
            logger.info("[ORCHESTRATOR] Step 4: Checking deduplication...")
            should_skip = self.deduplicator.should_skip(enhanced_commentary)
            
            if should_skip:
                logger.info("[ORCHESTRATOR] ✗ Commentary skipped (too similar to recent)")
                return {
                    "commentary": None,
                    "raw_action": raw_action,
                    "timestamp": current_time,
                    "skipped": True
                }
            
            self.deduplicator.add_commentary(enhanced_commentary, current_time)
            
            logger.info("[ORCHESTRATOR] ✓ Commentary accepted and added to history")
            
            return {
                "commentary": enhanced_commentary,
                "raw_action": raw_action,
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
    
    def clear_history(self):
        self.deduplicator.clear_history()
        logger.info("[ORCHESTRATOR] History cleared")
