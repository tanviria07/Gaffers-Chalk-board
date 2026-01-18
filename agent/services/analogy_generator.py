
import google.generativeai as genai
import os
import asyncio
from typing import Optional


class AnalogyGenerator:
    
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                try:
                    # Try model from .env first
                    self.model = genai.GenerativeModel(self.model_name)
                except Exception:
                    self.model_name = "gemini-1.5-pro"
                    self.model = genai.GenerativeModel(self.model_name)


                print(f"[ANALOGY] Gemini initialized with {self.model_name}")

            except Exception as e:
                print(f"[ANALOGY] Warning: Could not initialize Gemini: {e}")
                self.model = None
        else:
            print("[ANALOGY] Gemini NOT initialized - GEMINI_API_KEY not set")

    
    async def generate(self, commentary: str) -> str:
        
        if not self.model:
            return self._generate_stub_analogy(commentary)
        
        try:
            prompt = f"""You are a sports analyst who explains soccer plays using NFL analogies for American football fans. Convert this soccer commentary into an NFL analogy that American football fans would understand:

"{commentary}"

Instructions:
- Use NFL terminology and concepts
- Compare soccer positions to NFL positions (e.g., striker = receiver making a catch, midfielder = quarterback, defender = linebacker)
- Keep it concise (2-3 sentences max)
- Make it engaging and easy to understand
- Focus on the tactical parallel between the sports

Respond with ONLY the NFL analogy, no preamble."""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 150,
                    }
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"[ANALOGY] Generation error: {e}")
            return self._generate_stub_analogy(commentary)
    
    def _generate_stub_analogy(self, commentary: str) -> str:
        
        import random
        

        commentary_lower = commentary.lower()
        
        if any(word in commentary_lower for word in ['press', 'pressing', 'pressure']):
            return "This is like an all-out blitz — sending extra defenders to force a quick decision and create pressure on the ball carrier."
        
        if any(word in commentary_lower for word in ['counter', 'break', 'sprint']):
            return "This is a pick-six moment! The team just won the ball and is racing forward before the defense can reset — speed and timing are everything."
        
        if any(word in commentary_lower for word in ['defensive', 'defend', 'compact']):
            return "The defense is in prevent mode — staying compact, protecting the middle, and forcing the offense to make mistakes."
        
        if any(word in commentary_lower for word in ['attack', 'forward', 'goal']):
            return "This is like a well-designed red zone play — the offense is probing for weaknesses, creating space, and looking for the perfect moment to strike."
        

        return "This play is like a well-designed offensive scheme — every player has a role, creating space and options, waiting for the defense to make a mistake."
