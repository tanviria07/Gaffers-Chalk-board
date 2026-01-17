
import yt_dlp
import cv2
import base64
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class YouTubeFrameExtractor:
    
    
    def __init__(self):


        self.ydl_opts = {
            'format': 'best[ext=mp4][height<=720]/best[ext=webm][height<=720]/best[height<=720]/worst',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    async def extract_frame(self, video_url_or_id: str, timestamp: float) -> Optional[str]:
        
        try:

            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(
                None, 
                self._extract_frame_sync, 
                video_url_or_id, 
                timestamp
            )
            return frame
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return None
    
    async def extract_frames_range(self, video_url_or_id: str, start_time: float, end_time: float, sample_interval: float = 1.0) -> list[tuple[float, Optional[str]]]:
        

        frame_times = []
        current_time = start_time
        

        midpoint = (start_time + end_time) / 2
        
        while current_time <= end_time:
            frame_times.append(current_time)
            current_time += sample_interval
        

        if midpoint not in frame_times and midpoint != start_time and midpoint != end_time:
            frame_times.append(midpoint)
        
        frame_times.sort()
        

        async def extract_single_frame(timestamp: float) -> tuple[float, Optional[str]]:
            try:
                frame = await self.extract_frame(video_url_or_id, timestamp)
                return (timestamp, frame)
            except Exception as e:
                logger.error(f"Error extracting frame at {timestamp}s: {e}")
                return (timestamp, None)
        

        frame_results = await asyncio.gather(*[extract_single_frame(t) for t in frame_times], return_exceptions=True)
        

        frames = [
            (t, f) for t, f in frame_results
            if f and not isinstance(f, Exception)
        ]
        
        frames.sort(key=lambda x: x[0])
        return frames
    
    def _extract_frame_sync(self, video_url_or_id: str, timestamp: float) -> Optional[str]:
        
        cap = None
        try:

            if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
                video_url = video_url_or_id
            else:

                video_url = f"https://www.youtube.com/watch?v={video_url_or_id}"
            logger.info(f"Extracting frame from {video_url[:50]}... at {timestamp}s")
            

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(video_url, download=False)
                    if not info or 'url' not in info:
                        logger.error(f"Failed to get stream URL for {video_url[:50]}...")
                        return None
                    stream_url = info['url']
                    

                    if stream_url and ('.m3u8' in stream_url or 'manifest' in stream_url.lower()):
                        logger.warning(f"HLS stream detected (OpenCV may fail), trying alternative format...")

                        formats = info.get('formats', [])
                        for fmt in formats:
                            fmt_url = fmt.get('url', '')
                            if fmt_url and '.m3u8' not in fmt_url and 'manifest' not in fmt_url.lower():

                                if fmt.get('vcodec') != 'none':
                                    stream_url = fmt_url
                                    logger.info(f"Using non-HLS format: {fmt.get('format_id', 'unknown')}")
                                    break
                except Exception as e:
                    logger.error(f"yt-dlp extraction error: {e}")
                    return None
            
            if not stream_url:
                logger.error(f"No valid stream URL found for {video_url[:50]}...")
                return None
            

            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video stream for {video_url[:50]}... (URL: {stream_url[:100]}...)")
                return None
            

            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            

            success, frame = cap.read()
            
            if not success or frame is None:
                logger.warning(f"Failed to read frame at {timestamp}s for {video_url[:50]}...")
                return None
            

            height, width = frame.shape[:2]
            aspect_ratio = width / height
            

            max_size = 800
            if aspect_ratio > 1:

                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:

                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 78]
            success, buffer = cv2.imencode('.jpg', frame_resized, encode_param)
            
            if not success:
                logger.error("Failed to encode frame as JPEG")
                return None
            

            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            logger.info(f"Successfully extracted frame from {video_url[:50]}... at {timestamp}s")
            return base64_image
            
        except Exception as e:
            logger.error(f"Sync extraction error: {e}")
            return None
        finally:
            if cap is not None:
                cap.release()
