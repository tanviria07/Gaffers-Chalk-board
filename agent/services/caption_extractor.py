"""
YouTube Caption Extractor Service
Extracts captions/subtitles from YouTube videos using yt-dlp
"""
import yt_dlp
import asyncio
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class YouTubeCaptionExtractor:
    """Extract captions from YouTube videos"""
    
    def __init__(self):
        self.caption_cache: Dict[str, List[Dict]] = {}
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
    
    async def get_caption_at_timestamp(self, video_id: str, timestamp: float) -> Optional[str]:
        """
        Get caption text at a specific timestamp
        
        Args:
            video_id: YouTube video ID
            timestamp: Timestamp in seconds
        
        Returns:
            Caption text at timestamp, or None if not available
        """
        try:
            # Get all captions (cached)
            captions = await self.fetch_captions(video_id)
            
            if not captions:
                return None
            
            # Find caption at timestamp (with 3 second buffer)
            for caption in captions:
                start = float(caption.get('start', 0))
                duration = float(caption.get('duration', 0))
                end = start + duration
                
                # Check if timestamp falls within this caption
                if start <= timestamp <= end + 3:
                    return caption.get('text', '').strip()
            
            # Find nearest caption within 5 seconds
            nearest = None
            min_diff = 5.0
            
            for caption in captions:
                start = float(caption.get('start', 0))
                diff = abs(timestamp - start)
                if diff < min_diff:
                    min_diff = diff
                    nearest = caption
            
            if nearest:
                return nearest.get('text', '').strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting caption at timestamp: {e}")
            return None
    
    async def fetch_captions(self, video_id: str) -> List[Dict]:
        """
        Fetch all captions for a video (cached)
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            List of caption dictionaries with 'start', 'duration', 'text'
        """
        # Check cache first
        if video_id in self.caption_cache:
            logger.info(f"Using cached captions for {video_id}")
            return self.caption_cache[video_id]
        
        try:
            # Run blocking yt-dlp in thread pool with timeout
            loop = asyncio.get_event_loop()
            captions = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._fetch_captions_sync,
                    video_id
                ),
                timeout=3.0  # 3 second timeout
            )
            
            # Cache captions
            if captions:
                self.caption_cache[video_id] = captions
                logger.info(f"Cached {len(captions)} captions for {video_id}")
            
            return captions or []
            
        except asyncio.TimeoutError:
            logger.warning(f"Caption fetch timeout for {video_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching captions: {e}")
            return []
    
    def _fetch_captions_sync(self, video_id: str) -> List[Dict]:
        """
        Synchronous caption fetching (runs in thread pool)
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            List of caption dictionaries
        """
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(video_url, download=False)
                
                # Try to get automatic captions
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Prefer English subtitles, fallback to automatic captions
                caption_tracks = {}
                
                # Try English first
                if 'en' in subtitles:
                    caption_tracks = subtitles['en']
                elif 'en' in automatic_captions:
                    caption_tracks = automatic_captions['en']
                elif automatic_captions:
                    # Use first available language
                    first_lang = list(automatic_captions.keys())[0]
                    caption_tracks = automatic_captions[first_lang]
                elif subtitles:
                    # Use first available subtitle
                    first_lang = list(subtitles.keys())[0]
                    caption_tracks = subtitles[first_lang]
                
                if not caption_tracks:
                    logger.warning(f"No captions available for {video_id}")
                    return []
                
                # Get the first available caption URL
                caption_url = None
                for track in caption_tracks:
                    if track.get('ext') == 'vtt' or track.get('ext') == 'srv3':
                        caption_url = track.get('url')
                        break
                
                if not caption_url:
                    # Try any format
                    first_track = caption_tracks[0]
                    caption_url = first_track.get('url')
                
                if not caption_url:
                    logger.warning(f"No caption URL found for {video_id}")
                    return []
                
                # Download and parse captions
                import urllib.request
                import re
                
                response = urllib.request.urlopen(caption_url)
                vtt_content = response.read().decode('utf-8')
                
                # Parse VTT format
                captions = []
                pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\n\d{2}:|$)'
                
                for match in re.finditer(pattern, vtt_content, re.DOTALL):
                    start_str = match.group(1)
                    end_str = match.group(2)
                    text = match.group(3).strip()
                    
                    # Convert time to seconds
                    start_seconds = self._vtt_time_to_seconds(start_str)
                    end_seconds = self._vtt_time_to_seconds(end_str)
                    duration = end_seconds - start_seconds
                    
                    # Clean text (remove HTML tags, etc.)
                    text = re.sub(r'<[^>]+>', '', text)
                    text = re.sub(r'\n', ' ', text)
                    text = ' '.join(text.split())
                    
                    if text:
                        captions.append({
                            'start': start_seconds,
                            'duration': duration,
                            'text': text
                        })
                
                logger.info(f"Fetched {len(captions)} captions for {video_id}")
                return captions
                
        except Exception as e:
            logger.error(f"Sync caption fetch error: {e}")
            return []
    
    def _vtt_time_to_seconds(self, vtt_time: str) -> float:
        """Convert VTT time format (HH:MM:SS.mmm) to seconds"""
        try:
            parts = vtt_time.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
            return total_seconds
        except Exception:
            return 0.0
