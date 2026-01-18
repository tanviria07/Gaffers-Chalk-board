import os
import httpx
import asyncio
from typing import Optional


class TTSService:
    """
    Text-to-Speech service using ElevenLabs API.
    Returns audio as bytes (audio/mpeg).
    """

    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear, professional voice

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", self.DEFAULT_VOICE_ID)

        if self.api_key:
            print("[TTS] ElevenLabs initialized")
        else:
            print("[TTS] ElevenLabs NOT initialized - ELEVENLABS_API_KEY not set")

    def is_available(self) -> bool:
        """Check if TTS service is available."""
        return bool(self.api_key)

    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio bytes (MP3 format) or None if failed
        """
        if not text or not text.strip():
            print("[TTS] Empty text provided")
            return None

        if not self.api_key:
            print("[TTS] No API key available")
            return None

        url = f"{self.ELEVENLABS_API_URL}/{self.voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    print(f"[TTS] Successfully synthesized {len(text)} characters")
                    return response.content
                else:
                    print(f"[TTS] API error: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            print("[TTS] Request timed out")
            return None
        except Exception as e:
            print(f"[TTS] Error: {e}")
            return None
