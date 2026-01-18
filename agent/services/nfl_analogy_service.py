import google.generativeai as genai
import os
import asyncio
from typing import Optional, Tuple


class NFLAnalogyService:
    """
    Converts soccer commentary to NFL analogies and broadcast-style commentary.
    Uses two-step Gemini prompting for faithful, energetic output.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = None

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                try:
                    self.model = genai.GenerativeModel(self.model_name)
                except Exception:
                    self.model_name = "gemini-1.5-pro"
                    self.model = genai.GenerativeModel(self.model_name)
                print(f"[NFL-ANALOGY] Gemini initialized with {self.model_name}")
            except Exception as e:
                print(f"[NFL-ANALOGY] Warning: Could not initialize Gemini: {e}")
                self.model = None
        else:
            print("[NFL-ANALOGY] Gemini NOT initialized - GEMINI_API_KEY not set")

    async def generate_nfl_analogy(self, soccer_commentary: str) -> Tuple[str, str]:
        """
        Generate NFL analogy and NFL broadcast commentary from soccer commentary.

        Returns:
            Tuple of (nfl_analogy, nfl_commentary)
        """
        if not soccer_commentary or not soccer_commentary.strip():
            return ("", "")

        if not self.model:
            return self._generate_stub(soccer_commentary)

        try:
            nfl_analogy = await self._step1_soccer_to_analogy(soccer_commentary)
            nfl_commentary = await self._step2_analogy_to_broadcast(nfl_analogy)
            return (nfl_analogy, nfl_commentary)
        except Exception as e:
            print(f"[NFL-ANALOGY] Generation error: {e}")
            return self._generate_stub(soccer_commentary)

    async def _step1_soccer_to_analogy(self, soccer_commentary: str) -> str:
        """Step 1: Convert soccer commentary to NFL tactical analogy."""
        prompt = f"""You are a sports analyst converting soccer plays to NFL analogies.

SOCCER COMMENTARY:
"{soccer_commentary}"

RULES:
- Stay FAITHFUL to the soccer commentary - do NOT invent events that aren't described
- Do NOT use real NFL team names, player names, or stadium names
- Use ONLY generic terms: offense, defense, quarterback, receiver, linebacker, cornerback, safety, drive, snap, red zone, end zone, pocket, blitz, coverage, route, completion, sack, interception, touchdown
- Focus on the tactical parallel between what's happening in soccer and how it would translate to football

Write a 2-4 sentence tactical explanation using NFL concepts. Be precise and match the energy/stakes of the original soccer play.

Respond with ONLY the NFL analogy, no preamble or labels."""

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 200,
                }
            )
        )
        return response.text.strip()

    async def _step2_analogy_to_broadcast(self, nfl_analogy: str) -> str:
        """Step 2: Convert NFL analogy to energetic broadcast commentary."""
        prompt = f"""You are an NFL broadcast commentator. Convert this tactical analysis into exciting play-by-play style commentary.

NFL TACTICAL ANALYSIS:
"{nfl_analogy}"

RULES:
- Write 1-2 sentences, 15-35 words total
- Use energetic NFL broadcast style - punchy, dramatic, but NOT cringe or over-the-top
- Do NOT use real NFL team names, player names, or stadium names
- Keep it professional like a real NFL broadcast
- Match the intensity of the play being described

Respond with ONLY the broadcast commentary, no preamble or labels."""

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 100,
                }
            )
        )
        return response.text.strip()

    def _generate_stub(self, soccer_commentary: str) -> Tuple[str, str]:
        """Generate stub responses when Gemini is not available."""
        commentary_lower = soccer_commentary.lower()

        if any(word in commentary_lower for word in ['goal', 'score', 'net']):
            return (
                "The offense drove down the field with precision, finding the gap in the defense for a clean touchdown. The quarterback's patience paid off as the receiver broke free in the end zone.",
                "Touchdown! The offense finds the end zone after a methodical drive downfield!"
            )
        elif any(word in commentary_lower for word in ['save', 'block', 'keeper']):
            return (
                "The defense stood tall at the goal line, stuffing the run and forcing an incompletion on a critical fourth-down attempt. That's championship-caliber defense.",
                "What a defensive stand! The goal-line defense holds strong and denies the score!"
            )
        elif any(word in commentary_lower for word in ['pass', 'through', 'cross']):
            return (
                "The quarterback surveys the field and hits the receiver on a crossing route, threading the needle between two defenders. Great vision and execution.",
                "A perfectly placed throw across the middle! The receiver makes the catch in traffic!"
            )
        elif any(word in commentary_lower for word in ['counter', 'break', 'fast']):
            return (
                "The offense catches the defense in transition with a quick-hitting play. Before the secondary can recover, they're already past the first-down marker.",
                "The offense strikes fast on the counter! They caught the defense completely off-guard!"
            )
        else:
            return (
                "The offense methodically moves the chains, using a balanced attack to keep the defense guessing. Good protection up front gives the quarterback time to work.",
                "Steady progress on the drive as the offense continues to move the chains efficiently."
            )
