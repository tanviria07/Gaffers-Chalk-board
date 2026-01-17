from typing import List, Tuple, Optional
import asyncio
import logging
import os
import httpx
from services.youtube_extractor import YouTubeFrameExtractor

logger = logging.getLogger(__name__)


class FrameWindowService:
    
    def __init__(self):
        self.frame_extractor = YouTubeFrameExtractor()
        self.overshoot_service_url = os.getenv(
            "OVERSHOOT_SERVICE_URL", 
            "http://localhost:3002"
        )
        self.overshoot_enabled = os.getenv("OVERSHOOT_API_KEY") is not None
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def get_frame_window(
        self,
        video_url_or_id: str,
        current_time: float,
        window_size: float = 5.0,
        sample_interval: float = 1.5
    ) -> Tuple[List[str], List[float]]:
        if self.overshoot_enabled:
            try:
                logger.info(f"[FRAME WINDOW] Trying Overshoot for {video_url_or_id} at {current_time:.1f}s")
                frames, timestamps = await self._get_frames_from_overshoot(
                    video_url_or_id,
                    current_time,
                    window_size
                )
                if frames:
                    logger.info(f"[FRAME WINDOW] ✓ Got {len(frames)} frames from Overshoot")
                    return frames, timestamps
                else:
                    logger.warning("[FRAME WINDOW] Overshoot returned no frames, falling back to YouTube extractor")
            except Exception as e:
                logger.warning(f"[FRAME WINDOW] Overshoot failed: {e}, falling back to YouTube extractor")
        
        try:
            start_time = max(0, current_time - window_size)
            end_time = current_time
            
            logger.info(f"[FRAME WINDOW] Using YouTube extractor: {start_time:.1f}s - {end_time:.1f}s")
            
            frame_results = await self.frame_extractor.extract_frames_range(
                video_url_or_id,
                start_time,
                end_time,
                sample_interval=sample_interval
            )
            
            frames = []
            timestamps = []
            
            for timestamp, frame_base64 in frame_results:
                if frame_base64:
                    frames.append(frame_base64)
                    timestamps.append(timestamp)
            
            logger.info(f"[FRAME WINDOW] ✓ Extracted {len(frames)} frames from YouTube")
            
            if len(frames) == 0:
                logger.warning(f"[FRAME WINDOW] No frames, trying single frame at {current_time}s")
                single_frame = await self.frame_extractor.extract_frame(video_url_or_id, current_time)
                if single_frame:
                    frames = [single_frame]
                    timestamps = [current_time]
            
            return frames, timestamps
            
        except Exception as e:
            logger.error(f"[FRAME WINDOW] Error extracting window: {e}")
            import traceback
            traceback.print_exc()
            return [], []
    
    async def _get_frames_from_overshoot(
        self,
        video_url: str,
        current_time: float,
        window_size: float
    ) -> Tuple[List[str], List[float]]:
        try:
            response = await self.http_client.post(
                f"{self.overshoot_service_url}/get-frame-window",
                json={
                    "videoUrl": video_url,
                    "currentTime": current_time,
                    "windowSize": window_size
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    commentary = data.get("commentary") or data.get("rawAction")
                    if commentary:
                        logger.info(f"[OVERSHOOT] Got commentary: {commentary[:50]}...")
                        return [], []
                    else:
                        logger.warning("[OVERSHOOT] No commentary in response")
                        return [], []
                else:
                    logger.warning(f"[OVERSHOOT] Service error: {data.get('error')}")
                    return [], []
            elif response.status_code == 503:
                logger.warning("[OVERSHOOT] Service not available")
                return [], []
            elif response.status_code == 400:
                logger.warning(f"[OVERSHOOT] Invalid request: {response.text}")
                return [], []
            else:
                logger.warning(f"[OVERSHOOT] Service error: {response.status_code}")
                return [], []
                
        except httpx.RequestError as e:
            logger.warning(f"[OVERSHOOT] Connection error: {e}")
            return [], []
        except Exception as e:
            logger.error(f"[OVERSHOOT] Error: {e}")
            return [], []
