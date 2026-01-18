from typing import List, Tuple
import logging
import os
from services.youtube_extractor import YouTubeFrameExtractor

logger = logging.getLogger(__name__)


class FrameWindowService:

    def __init__(self):
        self.frame_extractor = YouTubeFrameExtractor()

    async def get_frame_window(
        self,
        video_url_or_id: str,
        current_time: float,
        window_size: float = 5.0,
        sample_interval: float = 1.5
    ) -> Tuple[List[str], List[float]]:
        try:
            start_time = max(0, current_time - window_size)
            end_time = current_time

            # Cap frame count for speed (default 4). You can override via env.
            # Example: FRAME_WINDOW_MAX_FRAMES=3
            max_frames = int(os.getenv("FRAME_WINDOW_MAX_FRAMES", "4"))
            max_frames = max(1, min(max_frames, 8))

            # Adjust interval to avoid too many frames inside the window.
            # If sample_interval already larger, keep it.
            if max_frames == 1:
                effective_interval = window_size  # basically one sample
            else:
                effective_interval = max(sample_interval, window_size / (max_frames - 1))

            logger.info(f"[FRAME WINDOW] Using YouTube extractor: {start_time:.1f}s - {end_time:.1f}s (interval={effective_interval:.2f}s, max_frames={max_frames})")

            frame_results = await self.frame_extractor.extract_frames_range(
                video_url_or_id,
                start_time,
                end_time,
                sample_interval=effective_interval
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
            logger.error(f"[FRAME WINDOW] Error extracting window: {e}", exc_info=True)
            return [], []
