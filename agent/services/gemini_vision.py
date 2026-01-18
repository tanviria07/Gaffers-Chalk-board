import os
import base64
import asyncio
from typing import List, Optional

import google.generativeai as genai
from utils.image_processor import compress_image


class GeminiVisionAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    async def analyze_frame_window(self, frames: List[str], timestamps: List[float]) -> str:
        if not self.model:
            raise RuntimeError("Gemini Vision not initialized. Set GEMINI_API_KEY and GEMINI_MODEL.")

        # Keep it light: max 4 frames
        pairs = list(zip(timestamps, frames))[:4]

        from PIL import Image
        import io

        imgs = []
        for ts, b64 in pairs:
            compressed = compress_image(b64, max_size=512, quality=55)
            img_bytes = base64.b64decode(compressed)
            imgs.append((ts, Image.open(io.BytesIO(img_bytes))))

        ts_line = ", ".join([f"{t:.1f}s" for t, _ in imgs])

        prompt = f"""
You are analyzing a soccer broadcast using a short sequence of frames.
Frame timestamps: {ts_line}

Describe what's happening in the play.
Mention ball location and main action (press, pass, shot, save, tackle, cross, set piece).
Do not invent player names.

Return 1–2 sentences, max 35 words.
"""

        content = [prompt] + [img for _, img in imgs]

        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: self.model.generate_content(content))
        text = (resp.text or "").strip()

        if not text:
            raise RuntimeError("Gemini returned empty vision response.")

        return text
