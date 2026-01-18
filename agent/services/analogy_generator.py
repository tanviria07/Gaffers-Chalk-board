
import anthropic
import os
from typing import Optional


class AnalogyGenerator:
    
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.client = None
    
    async def generate(self, commentary: str) -> str:
        
        if not self.client:
            return self._generate_stub_analogy(commentary)
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": f"You are a sports analyst who explains soccer plays using NFL analogies for American football fans. Convert this soccer commentary into an NFL analogy that American football fans would understand:\n\n\"{commentary}\"\n\nInstructions:\n- Use NFL terminology and concepts\n- Compare soccer positions to NFL positions (e.g., striker = receiver making a catch, midfielder = quarterback, defender = linebacker)\n- Keep it concise (2-3 sentences max)\n- Make it engaging and easy to understand\n- Focus on the tactical parallel between the sports\n\nRespond with ONLY the NFL analogy, no preamble."
                }]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            print(f"Analogy generation error: {e}")
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
