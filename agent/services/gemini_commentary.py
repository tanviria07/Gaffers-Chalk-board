import os
import google.generativeai as genai
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class GeminiCommentaryEnhancer:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("[GEMINI COMMENTARY] Initialized with gemini-1.5-flash")
            except Exception as e:
                logger.error(f"[GEMINI COMMENTARY] Failed to initialize: {e}")
                self.model = None
        else:
            logger.warning("[GEMINI COMMENTARY] No API key provided - will use stub responses")
    
    async def enhance_commentary(
        self,
        raw_action: str,
        style: str = "Broadcast",
        detail_level: str = "Normal"
    ) -> str:
        if not self.model or not raw_action:
            return self._enhance_stub(raw_action)
        
        try:
            prompt = f

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 100,
                    }
                )
            )
            
            commentary = response.text.strip()
            
            commentary = commentary.strip('"').strip("'").strip()
            
            logger.info(f"[GEMINI COMMENTARY] Enhanced: {commentary[:60]}...")
            return commentary
            
        except Exception as e:
            logger.error(f"[GEMINI COMMENTARY] Error enhancing commentary: {e}")
            import traceback
            traceback.print_exc()
            return self._enhance_stub(raw_action)
    
    def _enhance_stub(self, raw_action: str) -> str:
        if not raw_action:
            return "Players are moving into position, creating space for a potential attack."
        
        enhancements = {
            "press": "Relentless pressure there",
            "clearance": "forces the clearance",
            "pass": "slips a pass",
            "run": "makes a run",
            "tackle": "wins the ball",
        }
        
        for key, phrase in enhancements.items():
            if key in raw_action.lower():
                return f"{phrase} — {raw_action.lower()}"
        
        return f"Good action there — {raw_action.lower()}"
