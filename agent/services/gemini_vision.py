import os
import google.generativeai as genai
from typing import List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class GeminiVisionAnalyzer:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("[GEMINI VISION] Initialized with gemini-1.5-flash")
            except Exception as e:
                logger.error(f"[GEMINI VISION] Failed to initialize: {e}")
                self.model = None
        else:
            logger.warning("[GEMINI VISION] No API key provided - will use stub responses")
    
    async def analyze_frame_window(
        self, 
        frames: List[str], 
        timestamps: List[float]
    ) -> str:
        if not self.model or not frames:
            return self._generate_stub_action()
        
        try:
            prompt = 

            if len(frames) > 1:
                images = []
                for frame_base64 in frames:
                    import base64
                    from PIL import Image
                    import io
                    
                    image_data = base64.b64decode(frame_base64)
                    image = Image.open(io.BytesIO(image_data))
                    images.append(image)
                
                content = [prompt] + images
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(content)
                )
            else:
                import base64
                from PIL import Image
                import io
                
                image_data = base64.b64decode(frames[0])
                image = Image.open(io.BytesIO(image_data))
                
                content = [prompt, image]
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(content)
                )
            
            raw_action = response.text.strip()
            
            words = raw_action.split()
            if len(words) > 15:
                raw_action = " ".join(words[:15])
            
            logger.info(f"[GEMINI VISION] Generated raw action: {raw_action[:50]}...")
            return raw_action
            
        except Exception as e:
            logger.error(f"[GEMINI VISION] Error analyzing frames: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_stub_action()
    
    async def analyze_single_frame(self, frame_base64: str) -> str:
        return await self.analyze_frame_window([frame_base64], [0.0])
    
    def _generate_stub_action(self) -> str:
        import random
        stubs = [
            "Winger drives inside and slips a pass to the overlapping fullback.",
            "High press wins the ball and forces a rushed clearance.",
            "Striker's run is caught offside as the line steps up.",
            "Defensive line steps up well to deny space in behind.",
            "Counter-attack developing with players sprinting forward.",
        ]
        return random.choice(stubs)
