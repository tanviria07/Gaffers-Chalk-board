
from typing import Optional, Any, Dict
import time


class CacheManager:
    
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_expire = 300
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        

        if 'expires_at' in entry:
            if time.time() > entry['expires_at']:

                del self.cache[key]
                return None
        
        return entry.get('value')
    
    def set(self, key: str, value: Any, expire: int = None) -> None:
        
        expire_time = expire or self.default_expire
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + expire_time,
            'created_at': time.time()
        }
    
    def clear(self) -> None:
        
        self.cache.clear()
    
    def clear_expired(self) -> int:
        
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if 'expires_at' in entry and current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        
        return len(self.cache)
