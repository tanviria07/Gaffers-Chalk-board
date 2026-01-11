"""
YouTube Frame Extractor Service
Extracts frames from YouTube videos at specific timestamps using yt-dlp and OpenCV
"""
import yt_dlp
import cv2
import base64
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class YouTubeFrameExtractor:
    """Extract frames from YouTube videos at specific timestamps"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'worst[height<=480]',  # Use 480p for faster extraction
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    async def extract_frame(self, video_id: str, timestamp: float) -> Optional[str]:
        """
        Extract a single frame from YouTube video at given timestamp
        
        Args:
            video_id: YouTube video ID
            timestamp: Timestamp in seconds
        
        Returns:
            Base64 encoded JPEG image, or None if extraction fails
        """
        try:
            # Run blocking yt-dlp in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(
                None, 
                self._extract_frame_sync, 
                video_id, 
                timestamp
            )
            return frame
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return None
    
    def _extract_frame_sync(self, video_id: str, timestamp: float) -> Optional[str]:
        """
        Synchronous frame extraction (runs in thread pool)
        
        Args:
            video_id: YouTube video ID
            timestamp: Timestamp in seconds
        
        Returns:
            Base64 encoded JPEG image, or None if extraction fails
        """
        cap = None
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Extracting frame from {video_id} at {timestamp}s")
            
            # Get video stream URL using yt-dlp
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(video_url, download=False)
                    if not info or 'url' not in info:
                        logger.error(f"Failed to get stream URL for {video_id}")
                        return None
                    stream_url = info['url']
                except Exception as e:
                    logger.error(f"yt-dlp extraction error: {e}")
                    return None
            
            # Open video stream with OpenCV
            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video stream for {video_id}")
                return None
            
            # Seek to timestamp (convert to milliseconds)
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            
            # Read frame
            success, frame = cap.read()
            
            if not success or frame is None:
                logger.warning(f"Failed to read frame at {timestamp}s for {video_id}")
                return None
            
            # Resize for API efficiency (384x384 for faster processing)
            height, width = frame.shape[:2]
            aspect_ratio = width / height
            
            # Use smaller size for faster processing
            max_size = 384
            if aspect_ratio > 1:
                # Landscape: width is larger
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                # Portrait or square: height is larger
                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # Encode as JPEG with 50% quality for faster upload
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
            success, buffer = cv2.imencode('.jpg', frame_resized, encode_param)
            
            if not success:
                logger.error("Failed to encode frame as JPEG")
                return None
            
            # Convert to base64
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            logger.info(f"Successfully extracted frame from {video_id} at {timestamp}s")
            return base64_image
            
        except Exception as e:
            logger.error(f"Sync extraction error: {e}")
            return None
        finally:
            if cap is not None:
                cap.release()
