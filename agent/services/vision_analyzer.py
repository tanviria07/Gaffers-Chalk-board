"""
Vision AI service for analyzing video frames
"""
import anthropic
import os
from typing import Optional, Dict, Any
from utils.image_processor import compress_image


class VisionAnalyzer:
    """Analyzes video frames using Claude Vision API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.client = None
    
    async def analyze(self, base64_image: str) -> str:
        """
        Analyze video frame and extract what's happening (alias for analyze_frame)
        
        Args:
            base64_image: Base64 encoded image of video frame
        
        Returns:
            Commentary string describing the frame
        """
        return await self.analyze_frame(base64_image)
    
    async def analyze_frame(self, base64_image: str) -> str:
        """
        Analyze video frame and extract what's happening
        
        Args:
            base64_image: Base64 encoded image of video frame
        
        Returns:
            Commentary string describing the frame
        """
        if not self.client:
            return self._generate_stub_commentary()
        
        try:
            # Image is already compressed by YouTube extractor (384px, 50% quality)
            # Only compress further if image is still too large
            compressed = compress_image(base64_image, max_size=384, quality=50)
            
            # Call Claude Vision API
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fast & cost-effective
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": compressed
                            }
                        },
                        {
                            "type": "text",
                            "text": """You are a soccer commentator. Analyze this match frame and describe what's happening in 1-2 sentences.

Focus on:
- Key tactical moment or action
- Player positions and movements  
- Ball location
- Immediate threat or opportunity

Be specific and exciting, like live commentary."""
                        }
                    ]
                }]
            )
            
            commentary = message.content[0].text.strip()
            return commentary
            
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return self._generate_stub_commentary()
    
    async def extract_positions(self, base64_image: str) -> Dict[str, Any]:
        """
        Extract player positions for field diagram
        
        Args:
            base64_image: Base64 encoded image of video frame
        
        Returns:
            Dictionary with player positions and diagram type
        """
        # TODO: Implement actual position extraction using vision AI
        # For now, return mock data
        return {
            "attackers": [[0.7, 0.5], [0.6, 0.3], [0.65, 0.4]],
            "defenders": [[0.3, 0.5], [0.2, 0.7], [0.25, 0.6]],
            "ball": [0.65, 0.45],
            "diagramType": "defensive"
        }
    
    def _generate_stub_commentary(self) -> str:
        """Generate stub commentary when API is not available"""
        import random
        stubs = [
            "Players are moving into position, creating space for a potential attack.",
            "The team is building up play from the back, looking for passing options.",
            "A counter-attack is developing with players sprinting forward.",
            "Defensive shape is compact, denying space in the central areas.",
            "The ball is in the final third, with attackers looking for an opening."
        ]
        return random.choice(stubs)
