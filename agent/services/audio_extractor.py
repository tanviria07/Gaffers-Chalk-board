
import yt_dlp
import asyncio
import subprocess
import os
import tempfile
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioExtractor:
    
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'worstaudio/worst',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            from services.gemini_audio_transcriber import GeminiAudioTranscriber
            self.gemini_transcriber = GeminiAudioTranscriber()
        except Exception as e:
            logger.warning(f"[AUDIO EXTRACTOR] Could not initialize Gemini transcriber: {e}")
            self.gemini_transcriber = None
    
    def _get_video_url(self, video_url_or_id: str) -> str:
        
        if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
            return video_url_or_id
        return f"https://www.youtube.com/watch?v={video_url_or_id}"
    
    async def extract_audio_segment(self, video_url_or_id: str, start_time: float, end_time: float) -> Optional[str]:
        
        try:
            video_url = self._get_video_url(video_url_or_id)
            duration = end_time - start_time
            

            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_audio_path = temp_audio.name
            temp_audio.close()
            

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._extract_audio_sync,
                video_url,
                start_time,
                duration,
                temp_audio_path
            )
            
            return temp_audio_path
            
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return None
    
    def _extract_audio_sync(self, video_url: str, start_time: float, duration: float, output_path: str):
        
        try:

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info or 'url' not in info:
                    logger.error(f"Failed to get stream URL for audio extraction")
                    return None
                stream_url = info['url']
            


            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', stream_url,
                '-t', str(duration),
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr.decode()}")
                return None
            
            logger.info(f"Extracted audio segment: {start_time}s to {start_time + duration}s")
            return output_path
            
        except Exception as e:
            logger.error(f"Sync audio extraction error: {e}")
            return None
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "en-US") -> Optional[str]:
        
        if not self.gemini_transcriber or not self.gemini_transcriber.model:
            logger.warning("[AUDIO EXTRACTOR] Gemini transcriber not available, skipping audio transcription")
            return None
        
        try:
            transcript = await self.gemini_transcriber.transcribe_audio_file(audio_file_path)
            return transcript
                    
        except Exception as e:
            logger.error(f"[AUDIO EXTRACTOR] Audio transcription error: {e}")
            return None
        finally:
            try:
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
            except:
                pass
    
    async def extract_and_transcribe(self, video_url_or_id: str, start_time: float, end_time: float) -> Optional[str]:
        
        audio_path = await self.extract_audio_segment(video_url_or_id, start_time, end_time)
        if not audio_path:
            return None
        
        transcript = await self.transcribe_audio(audio_path)
        return transcript
