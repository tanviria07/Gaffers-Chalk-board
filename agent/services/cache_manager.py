"""
Cache manager for storing analysis results
"""
from typing import Optional, Any, Dict
import time


class CacheManager:
    """
    Simple in-memory cache with expiration support.
    For production, consider using Redis.
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_expire = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value if it exists and hasn't expired
        
        Args:
            key: Cache key (format: "videoId:timestamp")
        
        Returns:
            Cached value or None
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if 'expires_at' in entry:
            if time.time() > entry['expires_at']:
                # Expired, remove it
                del self.cache[key]
                return None
        
        return entry.get('value')
    
    def set(self, key: str, value: Any, expire: int = None) -> None:
        """
        Store value in cache with optional expiration
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (default: 5 minutes)
        """
        expire_time = expire or self.default_expire
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + expire_time,
            'created_at': time.time()
        }
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
    
    def clear_expired(self) -> int:
        """
        Remove expired entries and return count of removed items
        
        Returns:
            Number of expired entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if 'expires_at' in entry and current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Get number of cached entries"""
        return len(self.cache)
