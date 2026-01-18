
import yt_dlp
import asyncio
from typing import Optional, List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class YouTubeCaptionExtractor:
    
    
    def __init__(self):
        self.caption_cache: Dict[str, List[Dict]] = {}
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
        }
        
        self.audio_extractor = None
        try:
            from services.audio_extractor import AudioExtractor
            self.audio_extractor = AudioExtractor()
            logger.info("[CAPTION EXTRACTOR] Audio transcription fallback enabled (Gemini)")
        except ImportError:
            logger.warning("[CAPTION EXTRACTOR] AudioExtractor not available - audio transcription fallback disabled")
    
    def _get_cache_key(self, video_url_or_id: str) -> str:
        
        if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
            return video_url_or_id

        return f"https://www.youtube.com/watch?v={video_url_or_id}"
    
    async def get_caption_at_timestamp(self, video_url_or_id: str, timestamp: float, use_speech_fallback: bool = True) -> Optional[str]:
        
        try:

            captions = await self.fetch_captions(video_url_or_id)
            
            if not captions:
                if use_speech_fallback and self.audio_extractor:
                    logger.info(f"[CAPTION EXTRACTOR] No YouTube captions found, trying Gemini audio transcription at {timestamp}s...")
                    return await self._get_caption_from_speech(video_url_or_id, timestamp)
                return None
            

            for caption in captions:
                start = float(caption.get('start', 0))
                duration = float(caption.get('duration', 0))
                end = start + duration
                

                if start <= timestamp <= end + 3:
                    return caption.get('text', '').strip()
            

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
            
            if use_speech_fallback and self.audio_extractor:
                logger.info(f"[CAPTION EXTRACTOR] No caption at {timestamp}s, trying Gemini audio transcription...")
                return await self._get_caption_from_speech(video_url_or_id, timestamp)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting caption at timestamp: {e}")
            if use_speech_fallback and self.audio_extractor:
                try:
                    return await self._get_caption_from_speech(video_url_or_id, timestamp)
                except Exception as fallback_error:
                    logger.error(f"Speech-to-text fallback also failed: {fallback_error}")
            return None
    
    async def _get_caption_from_speech(self, video_url_or_id: str, timestamp: float, window_size: float = 5.0) -> Optional[str]:
        
        try:
            start_time = max(0.0, timestamp - window_size / 2)
            end_time = timestamp + window_size / 2
            
            transcript = await self.audio_extractor.extract_and_transcribe(
                video_url_or_id,
                start_time,
                end_time
            )
            
            if transcript:
                logger.info(f"[CAPTION EXTRACTOR] ✓ Gemini audio transcription: {transcript[:60]}...")
                return transcript.strip()
            else:
                logger.warning(f"[CAPTION EXTRACTOR] Gemini audio transcription returned no transcript")
                return None
                
        except Exception as e:
            logger.error(f"[CAPTION EXTRACTOR] Gemini audio transcription error: {e}")
            return None
    
    async def get_captions_in_range(self, video_url_or_id: str, start_time: float, end_time: float, use_speech_fallback: bool = True) -> List[Dict]:
        
        try:

            captions = await self.fetch_captions(video_url_or_id)
            
            if not captions:
                if use_speech_fallback and self.audio_extractor:
                    logger.info(f"[CAPTION EXTRACTOR] No YouTube captions found, generating Gemini audio transcription for range {start_time}s-{end_time}s...")
                    speech_caption = await self._get_caption_from_speech(video_url_or_id, (start_time + end_time) / 2, window_size=end_time - start_time)
                    if speech_caption:
                        return [{
                            'start': start_time,
                            'duration': end_time - start_time,
                            'text': speech_caption,
                            'source': 'gemini-audio'
                        }]
                return []
            

            captions_in_range = []
            for caption in captions:
                start = float(caption.get('start', 0))
                duration = float(caption.get('duration', 0))
                end = start + duration
                

                if not (end < start_time or start > end_time):
                    captions_in_range.append(caption)
            
            if not captions_in_range and use_speech_fallback and self.audio_extractor:
                logger.info(f"[CAPTION EXTRACTOR] No captions in range, trying Gemini audio transcription...")
                speech_caption = await self._get_caption_from_speech(video_url_or_id, (start_time + end_time) / 2, window_size=end_time - start_time)
                if speech_caption:
                    return [{
                        'start': start_time,
                        'duration': end_time - start_time,
                        'text': speech_caption,
                        'source': 'gemini-audio'
                    }]
            
            return captions_in_range
            
        except Exception as e:
            logger.error(f"Error getting captions in range: {e}")
            return []
    
    async def fetch_captions(self, video_url_or_id: str) -> List[Dict]:
        
        cache_key = self._get_cache_key(video_url_or_id)
        

        if cache_key in self.caption_cache:
            logger.info(f"Using cached captions for {cache_key}")
            return self.caption_cache[cache_key]
        
        try:

            loop = asyncio.get_event_loop()
            captions = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._fetch_captions_sync,
                    video_url_or_id
                ),
                timeout=15.0
            )
            

            if captions:
                self.caption_cache[cache_key] = captions
                logger.info(f"Cached {len(captions)} captions for {cache_key}")
            else:
                logger.info(f"No YouTube captions found for {cache_key} - speech-to-text fallback available: {self.audio_extractor is not None}")
            
            return captions or []
            
        except asyncio.TimeoutError:
            logger.warning(f"Caption fetch timeout for {video_url_or_id} - speech-to-text fallback available: {self.audio_extractor is not None}")
            return []
        except Exception as e:
            logger.error(f"Error fetching captions: {e} - speech-to-text fallback available: {self.audio_extractor is not None}")
            return []
    
    def _fetch_captions_sync(self, video_url_or_id: str) -> List[Dict]:
        
        try:

            if video_url_or_id.startswith('http://') or video_url_or_id.startswith('https://'):
                video_url = video_url_or_id
            else:

                video_url = f"https://www.youtube.com/watch?v={video_url_or_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:

                info = ydl.extract_info(video_url, download=False)
                

                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                

                caption_tracks = {}
                

                if 'en' in subtitles:
                    caption_tracks = subtitles['en']
                elif 'en' in automatic_captions:
                    caption_tracks = automatic_captions['en']
                elif automatic_captions:

                    first_lang = list(automatic_captions.keys())[0]
                    caption_tracks = automatic_captions[first_lang]
                elif subtitles:

                    first_lang = list(subtitles.keys())[0]
                    caption_tracks = subtitles[first_lang]
                
                if not caption_tracks:
                    logger.warning(f"No captions available for {video_url} - speech-to-text fallback will be used if configured")
                    logger.warning(f"Available subtitles: {list(subtitles.keys()) if subtitles else 'none'}")
                    logger.warning(f"Available automatic_captions: {list(automatic_captions.keys()) if automatic_captions else 'none'}")
                    return []
                
                logger.info(f"Found caption tracks: {len(caption_tracks)} tracks available")
                

                caption_url = None
                for track in caption_tracks:
                    if track.get('ext') == 'vtt' or track.get('ext') == 'srv3':
                        caption_url = track.get('url')
                        logger.info(f"Selected caption track: ext={track.get('ext')}, name={track.get('name', 'unknown')}")
                        break
                
                if not caption_url:

                    first_track = caption_tracks[0]
                    caption_url = first_track.get('url')
                    logger.info(f"Using first available track: ext={first_track.get('ext')}, name={first_track.get('name', 'unknown')}")
                
                if not caption_url:
                    logger.warning(f"No caption URL found for {video_url}")
                    return []
                
                logger.info(f"Downloading captions from: {caption_url[:100]}...")
                

                import urllib.request
                import re
                import xml.etree.ElementTree as ET
                
                response = urllib.request.urlopen(caption_url)
                caption_content = response.read().decode('utf-8')
                
                captions = []
                

                if caption_content.strip().startswith('<?xml') or caption_content.strip().startswith('<transcript'):

                    logger.info("Detected XML caption format, parsing...")
                    try:

                        root = ET.fromstring(caption_content)
                        



                        

                        text_elements = root.findall('.//text')
                        if text_elements:
                            for elem in text_elements:
                                start_str = elem.get('start', '0')
                                dur_str = elem.get('dur', '0')
                                text = elem.text or ''
                                
                                try:
                                    start_seconds = float(start_str)
                                    duration = float(dur_str)
                                    


                                    text = re.sub(r'<[^>]+>', '', text)
                                    text = text.strip()
                                    
                                    if text:
                                        captions.append({
                                            'start': start_seconds,
                                            'duration': duration,
                                            'text': text
                                        })
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Error parsing caption timing: {e}")
                                    continue
                        

                        if not captions:
                            p_elements = root.findall('.//{http://www.w3.org/ns/ttml}p') or root.findall('.//p')
                            for elem in p_elements:
                                begin_str = elem.get('begin', '0')
                                end_str = elem.get('end', '0')
                                text = ''.join(elem.itertext()) if hasattr(elem, 'itertext') else (elem.text or '')
                                
                                try:
                                    start_seconds = self._parse_time_string(begin_str)
                                    end_seconds = self._parse_time_string(end_str)
                                    duration = end_seconds - start_seconds
                                    
                                    text = re.sub(r'<[^>]+>', '', text)
                                    text = text.strip()
                                    
                                    if text:
                                        captions.append({
                                            'start': start_seconds,
                                            'duration': duration,
                                            'text': text
                                        })
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Error parsing TTML caption timing: {e}")
                                    continue
                    
                    except ET.ParseError as e:
                        logger.error(f"XML parsing error: {e}")
                        logger.debug(f"First 500 chars of content: {caption_content[:500]}")
                
                else:

                    logger.info("Detected VTT caption format, parsing...")

                    pattern = r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})(?:[^\n]*\n)?(.*?)(?=\n\n|\n\d{2}:\d{2}:\d{2}|$)'
                    
                    for match in re.finditer(pattern, caption_content, re.DOTALL | re.MULTILINE):
                        start_str = match.group(1).replace(',', '.')
                        end_str = match.group(2).replace(',', '.')
                        text = match.group(3)
                        

                        start_seconds = self._vtt_time_to_seconds(start_str)
                        end_seconds = self._vtt_time_to_seconds(end_str)
                        duration = end_seconds - start_seconds
                        


                        text = re.sub(r'<[^>]+>', '', text)

                        text = re.sub(r'<c\.[^>]+>', '', text)

                        text = re.sub(r'<v[^>]*>', '', text)


                        text = text.strip()
                        
                        if text:
                            captions.append({
                                'start': start_seconds,
                                'duration': duration,
                                'text': text
                            })
                
                logger.info(f"Fetched {len(captions)} captions for {video_url}")
                if len(captions) > 0:
                    logger.info(f"Sample caption (first): start={captions[0]['start']:.2f}s, text='{captions[0]['text'][:50]}...'")
                else:
                    logger.warning(f"No captions parsed. Content preview (first 500 chars): {caption_content[:500]}")
                return captions
                
        except Exception as e:
            logger.error(f"Sync caption fetch error: {e}")
            return []
    
    def _vtt_time_to_seconds(self, vtt_time: str) -> float:
        
        try:

            vtt_time = vtt_time.replace(',', '.')
            parts = vtt_time.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
            return total_seconds
        except Exception as e:
            logger.error(f"Error parsing VTT time '{vtt_time}': {e}")
            return 0.0
    
    def _parse_time_string(self, time_str: str) -> float:
        
        try:

            if '.' in time_str or ',' in time_str:

                try:
                    return float(time_str.replace(',', '.'))
                except ValueError:
                    pass
            

            if ':' in time_str:
                return self._vtt_time_to_seconds(time_str)
            

            return float(time_str)
        except Exception as e:
            logger.error(f"Error parsing time string '{time_str}': {e}")
            return 0.0
