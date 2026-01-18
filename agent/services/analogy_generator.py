import os
import asyncio
from typing import Optional

from google import genai


class AnalogyGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = (os.getenv("GEMINI_MODEL") or "gemini-2.0-flash").strip()
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def generate(self, commentary: str) -> str:
        if not self.client:
            return self._generate_stub_analogy(commentary)

        prompt = (
            "You are a sports analyst who explains soccer plays using NFL analogies for American football fans. "
            "Convert this soccer commentary into an NFL analogy that American football fans would understand:\n\n"
            f"\"{commentary}\"\n\n"
            "Instructions:\n"
            "- Use NFL terminology and concepts\n"
            "- Compare soccer positions to NFL positions (e.g., striker = receiver making a catch, midfielder = quarterback, defender = linebacker)\n"
            "- Keep it concise (2-3 sentences max)\n"
            "- Make it engaging and easy to understand\n"
            "- Focus on the tactical parallel between the sports\n\n"
            "Respond with ONLY the NFL analogy, no preamble."
        )

        loop = asyncio.get_event_loop()
        model_try = [self.model_name, "gemini-2.0-flash", "gemini-1.5-pro"]

        last_err = None
        for m in model_try:
            try:
                resp = await loop.run_in_executor(
                    None, lambda: self.client.models.generate_content(model=m, contents=prompt)
                )
                text = (getattr(resp, "text", "") or "").strip()
                if text:
                    return text
                raise RuntimeError("Empty Gemini text response.")
            except Exception as e:
                last_err = e

        return self._generate_stub_analogy(commentary)

    def _generate_stub_analogy(self, commentary: str) -> str:
        commentary_lower = commentary.lower()

        if any(word in commentary_lower for word in ["press", "pressing", "pressure"]):
            return "This is like an all-out blitz — sending extra defenders to force a quick decision and create pressure on the ball carrier."

        if any(word in commentary_lower for word in ["counter", "break", "sprint"]):
            return "This is a pick-six moment! The team just won the ball and is racing forward before the defense can reset — speed and timing are everything."

        if any(word in commentary_lower for word in ["defensive", "defend", "compact"]):
            return "The defense is in prevent mode — staying compact, protecting the middle, and forcing the offense to make mistakes."

        if any(word in commentary_lower for word in ["attack", "forward", "goal"]):
            return "This is like a well-designed red zone play — the offense is probing for weaknesses, creating space, and looking for the perfect moment to strike."

        return "This play is like a well-designed offensive scheme — every player has a role, creating space and options, waiting for the defense to make a mistake."
