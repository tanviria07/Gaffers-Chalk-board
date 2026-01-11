"""
NFL Analogy Generator service
"""
import anthropic
import os
from typing import Optional


class AnalogyGenerator:
    """Generates NFL analogies from soccer commentary"""
    
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
        """
        Convert soccer commentary to NFL analogy
        
        Args:
            commentary: Soccer match commentary
        
        Returns:
            NFL analogy string
        """
        if not self.client:
            return self._generate_stub_analogy(commentary)
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": f"""You're an NFL commentator explaining soccer to American football fans.

Soccer moment: {commentary}

Convert this to an NFL analogy using:
- NFL positions (QB, RB, WR, linebacker, safety, cornerback)
- NFL plays (blitz, screen pass, play action, zone defense, man coverage)
- NFL field terms (A-gap, B-gap, red zone, pocket, shotgun)

Keep it under 30 words and make it exciting!"""
                }]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            print(f"Analogy generation error: {e}")
            return self._generate_stub_analogy(commentary)
    
    def _generate_stub_analogy(self, commentary: str) -> str:
        """Generate stub analogy when API is not available"""
        import random
        
        # Context-aware stub analogies
        commentary_lower = commentary.lower()
        
        if any(word in commentary_lower for word in ['press', 'pressing', 'pressure']):
            return "This is like an all-out blitz — sending extra defenders to force a quick decision and create pressure on the ball carrier."
        
        if any(word in commentary_lower for word in ['counter', 'break', 'sprint']):
            return "This is a pick-six moment! The team just won the ball and is racing forward before the defense can reset — speed and timing are everything."
        
        if any(word in commentary_lower for word in ['defensive', 'defend', 'compact']):
            return "The defense is in prevent mode — staying compact, protecting the middle, and forcing the offense to make mistakes."
        
        if any(word in commentary_lower for word in ['attack', 'forward', 'goal']):
            return "This is like a well-designed red zone play — the offense is probing for weaknesses, creating space, and looking for the perfect moment to strike."
        
        # Default analogy
        return "This play is like a well-designed offensive scheme — every player has a role, creating space and options, waiting for the defense to make a mistake."
