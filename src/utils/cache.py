from typing import Dict, Optional
from cachetools import TTLCache

class Cache:
    def __init__(self):
        """Initialize cache with TTL"""
        self.message_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL
        self.user_cache = TTLCache(maxsize=500, ttl=7200)      # 2 hours TTL

    def get_message(self, key: str) -> Optional[dict]:
        """Get message from cache"""
        return self.message_cache.get(key)

    def set_message(self, key: str, value: dict):
        """Set message in cache"""
        self.message_cache[key] = value

    def get_user(self, key: str) -> Optional[dict]:
        """Get user from cache"""
        return self.user_cache.get(key)

    def set_user(self, key: str, value: dict):
        """Set user in cache"""
        self.user_cache[key] = value 