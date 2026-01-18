import yt_dlp
import cv2
import base64
import asyncio
import time
from typing import Optional, Dict, Tuple
import logging
import threading

logger = logging.getLogger(__name__)


class YouTubeFrameExtractor:
    """
    Speed + stability improvements:
    - Resolve stream URL once per window, then extract multiple frames from the same URL.
    - Cache resolved stream URLs for a short TTL to avoid repeated yt-dlp hits (prevents 403 spam).
    """

    def __init__(self):
        self.ydl_opts = {
            "format": "best[ext=mp4][height<=720]/best[ext=webm][height<=720]/best[height<=720]/worst",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        # stream_url cache: key -> (stream_url, expires_at)
        self._stream_cache: Dict[str, Tuple[str, float]] = {}
        self._cache_lock = threading.Lock()
        self._default_ttl_seconds = 120  # keep small; stream URLs can expire

    def _normalize_video_url(self, video_url_or_id: str) -> str:
        if video_url_or_id.startswith("http://") or video_url_or_id.startswith("https://"):
            return video_url_or_id
        return f"https://www.youtube.com/watch?v={video_url_or_id}"

    def _cache_key(self, video_url: str) -> str:
        # Keep it simple: the full video URL is fine as a key
        return video_url

    def _get_cached_stream_url(self, key: str) -> Optional[str]:
        now = time.time()
        with self._cache_lock:
            item = self._stream_cache.get(key)
            if not item:
                return None
            stream_url, expires_at = item
            if expires_at <= now:
                self._stream_cache.pop(key, None)
                return None
            return stream_url

    def _set_cached_stream_url(self, key: str, stream_url: str, ttl: Optional[int] = None) -> None:
        ttl_seconds = self._default_ttl_seconds if ttl is None else max(5, int(ttl))
        expires_at = time.time() + ttl_seconds
        with self._cache_lock:
            self._stream_cache[key] = (stream_url, expires_at)

    async def get_stream_url(self, video_url_or_id: str) -> Optional[str]:
        """
        Resolve a direct stream URL (cached).
        """
        video_url = self._normalize_video_url(video_url_or_id)
        key = self._cache_key(video_url)

        cached = self._get_cached_stream_url(key)
        if cached:
            return cached

        loop = asyncio.get_event_loop()
        stream_url = await loop.run_in_executor(None, self._resolve_stream_url_sync, video_url)

        if stream_url:
            self._set_cached_stream_url(key, stream_url)

        return stream_url

    def _resolve_stream_url_sync(self, video_url: str) -> Optional[str]:
        """
        One yt-dlp call to get a usable non-HLS stream URL.
        """
        try:
            logger.info(f"Resolving stream URL via yt-dlp for {video_url[:60]}...")

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    logger.error("yt-dlp returned no info")
                    return None

                stream_url = info.get("url")
                if not stream_url:
                    logger.error("yt-dlp info missing 'url'")
                    return None

                # If HLS/manifest, pick an alternative format url
                if stream_url and (".m3u8" in stream_url or "manifest" in stream_url.lower()):
                    logger.warning("HLS stream detected (OpenCV may fail). Searching for non-HLS format...")
                    formats = info.get("formats", [])
                    for fmt in formats:
                        fmt_url = fmt.get("url", "")
                        if not fmt_url:
                            continue
                        if ".m3u8" in fmt_url or "manifest" in fmt_url.lower():
                            continue
                        # prefer video streams
                        if fmt.get("vcodec") != "none":
                            stream_url = fmt_url
                            logger.info(f"Using non-HLS format: {fmt.get('format_id', 'unknown')}")
                            break

                return stream_url

        except Exception as e:
            logger.error(f"yt-dlp resolve error: {e}")
            return None

    async def extract_frame(self, video_url_or_id: str, timestamp: float) -> Optional[str]:
        """
        Backwards compatible: still works.
        Now uses cached stream URL so it doesn't hammer yt-dlp every time.
        """
        try:
            stream_url = await self.get_stream_url(video_url_or_id)
            if not stream_url:
                return None

            video_url = self._normalize_video_url(video_url_or_id)

            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(
                None,
                self._extract_frame_from_stream_sync,
                stream_url,
                video_url,
                timestamp,
            )
            return frame
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return None

    async def extract_frames_range(
        self,
        video_url_or_id: str,
        start_time: float,
        end_time: float,
        sample_interval: float = 1.0
    ) -> list[tuple[float, Optional[str]]]:
        """
        Fast path:
        - Resolve stream once
        - Extract frames concurrently from the same stream
        """
        # Build timestamps
        frame_times = []
        current_time = start_time
        midpoint = (start_time + end_time) / 2

        while current_time <= end_time:
            frame_times.append(current_time)
            current_time += sample_interval

        if midpoint not in frame_times and midpoint != start_time and midpoint != end_time:
            frame_times.append(midpoint)

        frame_times = sorted(set(frame_times))

        # Resolve stream URL once for the whole window
        stream_url = await self.get_stream_url(video_url_or_id)
        if not stream_url:
            return []

        video_url = self._normalize_video_url(video_url_or_id)

        loop = asyncio.get_event_loop()

        async def extract_single_frame(t: float) -> tuple[float, Optional[str]]:
            try:
                frame = await loop.run_in_executor(
                    None,
                    self._extract_frame_from_stream_sync,
                    stream_url,
                    video_url,
                    t,
                )
                return (t, frame)
            except Exception as e:
                logger.error(f"Error extracting frame at {t}s: {e}")
                return (t, None)

        # Limit concurrency a bit (prevents OpenCV overload on some machines)
        sem = asyncio.Semaphore(3)

        async def bounded_extract(t: float):
            async with sem:
                return await extract_single_frame(t)

        results = await asyncio.gather(*[bounded_extract(t) for t in frame_times], return_exceptions=False)

        frames = [(t, f) for (t, f) in results if f]
        frames.sort(key=lambda x: x[0])
        return frames

    def _extract_frame_from_stream_sync(self, stream_url: str, video_url_for_log: str, timestamp: float) -> Optional[str]:
        cap = None
        try:
            logger.info(f"Extracting frame from {video_url_for_log[:60]}... at {timestamp:.2f}s")

            cap = cv2.VideoCapture(stream_url)
            if not cap.isOpened():
                logger.error(f"Failed to open stream (first 120 chars): {stream_url[:120]}")
                return None

            cap.set(cv2.CAP_PROP_POS_MSEC, float(timestamp) * 1000.0)

            success, frame = cap.read()
            if not success or frame is None:
                logger.warning(f"Failed to read frame at {timestamp:.2f}s")
                return None

            height, width = frame.shape[:2]
            aspect_ratio = width / height if height else 1.0

            max_size = 640
            if aspect_ratio > 1:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)

            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 78]
            success, buffer = cv2.imencode(".jpg", frame_resized, encode_param)
            if not success:
                logger.error("Failed to encode frame as JPEG")
                return None

            return base64.b64encode(buffer).decode("utf-8")

        except Exception as e:
            logger.error(f"Sync extraction error: {e}")
            return None
        finally:
            if cap is not None:
                cap.release()
