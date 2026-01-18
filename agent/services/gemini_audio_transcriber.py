import os
import google.generativeai as genai
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class GeminiAudioTranscriber:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        # Use env if present, otherwise default to a valid model
        self.model_name = os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"

        self.model = None

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                try:
                    # Try env/default model first
                    self.model = genai.GenerativeModel(self.model_name)
                except Exception:
                    # Fallback to a different model if the first fails
                    self.model_name = "gemini-1.5-pro"
                    self.model = genai.GenerativeModel(self.model_name)

                logger.info(f"[GEMINI AUDIO] Initialized with {self.model_name}")

            except Exception as e:
                logger.error(f"[GEMINI AUDIO] Failed to initialize: {e}")
                self.model = None
        else:
            logger.warning("[GEMINI AUDIO] No API key provided - will return None")

    
    async def transcribe_audio_file(self, audio_file_path: str, prompt: Optional[str] = None) -> Optional[str]:
        if not self.model or not audio_file_path:
            return None
        
        if not os.path.exists(audio_file_path):
            logger.error(f"[GEMINI AUDIO] Audio file not found: {audio_file_path}")
            return None
        
        try:
            default_prompt = "Transcribe this soccer commentary audio. Keep it natural and include all words spoken. Focus on describing the action, goals, saves, and player movements."
            transcription_prompt = prompt or default_prompt
            
            loop = asyncio.get_event_loop()
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                
                content = [
                    {
                        "mime_type": "audio/wav",
                        "data": audio_data
                    },
                    transcription_prompt
                ]
                
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(content)
                )
                
                transcript = response.text.strip()
                logger.info(f"[GEMINI AUDIO] ✓ Transcribed: {transcript[:60]}...")
                return transcript
                
        except Exception as e:
            logger.error(f"[GEMINI AUDIO] Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            return None