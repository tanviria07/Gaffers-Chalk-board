
import yt_dlp
import asyncio
from typing import Optional, Dict, Any
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoMetadataExtractor:
    
    
    def __init__(self):
        self.metadata_cache: Dict[str, Dict[str, Any]] = {}
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        }
    
    def _get_cache_key(self, video_url_or_id: str) -> str:
        
        if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
            return video_url_or_id

        return f"https://www.youtube.com/watch?v={video_url_or_id}"
    
    async def get_metadata(self, video_url_or_id: str) -> Optional[Dict[str, Any]]:
        
        cache_key = self._get_cache_key(video_url_or_id)
        

        if cache_key in self.metadata_cache:
            logger.info(f"Using cached metadata for {cache_key}")
            return self.metadata_cache[cache_key]
        
        try:

            loop = asyncio.get_event_loop()
            metadata = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._extract_metadata_sync,
                    video_url_or_id
                ),
                timeout=10.0
            )
            

            if metadata:
                self.metadata_cache[cache_key] = metadata
                logger.info(f"Cached metadata for {cache_key}: {metadata.get('title', 'N/A')[:50]}")
            
            return metadata
            
        except asyncio.TimeoutError:
            logger.warning(f"Metadata extraction timeout for {video_url_or_id}")
            return None
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return None
    
    def _extract_metadata_sync(self, video_url_or_id: str) -> Optional[Dict[str, Any]]:
        
        try:

            if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
                video_url = video_url_or_id
            else:

                video_url = f"https://www.youtube.com/watch?v={video_url_or_id}"
            
            logger.info(f"Extracting metadata from {video_url[:50]}...")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    logger.error(f"Failed to extract info for {video_url[:50]}...")
                    return None
                

                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', '')[:500],
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'video_id': info.get('id', ''),
                    'url': video_url,
                }
                
                logger.info(f"Extracted metadata: {metadata['title'][:50]}...")
                return metadata
                
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return None
