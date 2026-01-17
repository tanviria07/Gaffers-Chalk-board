from typing import List, Tuple
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class CommentaryDeduplicator:
    
    def __init__(self, similarity_threshold: float = 0.85, max_history: int = 10):
        self.threshold = similarity_threshold
        self.max_history = max_history
        self.history: List[Tuple[str, float]] = []
    
    def should_skip(self, new_commentary: str) -> bool:
        if not new_commentary or not new_commentary.strip():
            return True
        
        if len(self.history) == 0:
            return False
        
        new_lower = new_commentary.lower().strip()
        
        for old_commentary, _ in self.history:
            old_lower = old_commentary.lower().strip()
            
            similarity = SequenceMatcher(None, new_lower, old_lower).ratio()
            
            if similarity >= self.threshold:
                logger.info(f"[DEDUP] Skipping similar commentary (similarity: {similarity:.2f})")
                logger.info(f"[DEDUP] Old: {old_commentary[:50]}...")
                logger.info(f"[DEDUP] New: {new_commentary[:50]}...")
                return True
        
        return False
    
    def add_commentary(self, commentary: str, timestamp: float):
        if not commentary or not commentary.strip():
            return
        
        self.history.append((commentary, timestamp))
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        logger.debug(f"[DEDUP] Added to history: {commentary[:50]}... (total: {len(self.history)})")
    
    def clear_history(self):
        self.history.clear()
        logger.info("[DEDUP] History cleared")
    
    def get_similarity_score(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
