import os
import base64
import asyncio
from typing import List, Optional

from google import genai
from google.genai import types

from utils.image_processor import compress_image


class GeminiVisionAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = (os.getenv("GEMINI_MODEL") or "gemini-2.0-flash").strip()
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def analyze_frame_window(self, frames: List[str], timestamps: List[float]) -> str:
        if not self.client:
            raise RuntimeError("Gemini Vision not initialized. Set GEMINI_API_KEY.")

        pairs = list(zip(timestamps, frames))[:4]
        parts = []

        ts_list = []
        for ts, b64 in pairs:
            compressed = compress_image(b64, max_size=512, quality=55)
            img_bytes = base64.b64decode(compressed)
            ts_list.append(f"{ts:.1f}s")
            parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))

        ts_line = ", ".join(ts_list)

        prompt = (
            "You are analyzing a soccer broadcast using a short sequence of frames.\n"
            f"Frame timestamps: {ts_line}\n\n"
            "Describe what's happening in the play.\n"
            "Mention ball location and main action (press, pass, shot, save, tackle, cross, set piece).\n"
            "Do not invent player names.\n\n"
            "Return 1–2 sentences, max 35 words."
        )

        contents = [prompt, *parts]

        loop = asyncio.get_event_loop()
        model_try = [self.model_name, "gemini-2.0-flash", "gemini-1.5-pro"]

        last_err = None
        for m in model_try:
            try:
                resp = await loop.run_in_executor(
                    None, lambda: self.client.models.generate_content(model=m, contents=contents)
                )
                text = (getattr(resp, "text", "") or "").strip()
                if not text:
                    raise RuntimeError("Empty Gemini vision response.")
                return text
            except Exception as e:
                last_err = e

        raise RuntimeError(f"Gemini vision failed: {last_err}")
