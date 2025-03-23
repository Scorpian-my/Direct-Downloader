import asyncio
from datetime import datetime, timedelta
from collections import deque
from typing import Optional

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    async def acquire(self):
        """Acquire a rate limit slot"""
        now = datetime.now()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.time_window):
            self.requests.popleft()
        
        # If we've hit the limit, wait
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Add current request
        self.requests.append(now)

    def get_wait_time(self) -> Optional[float]:
        """Get wait time if rate limit is hit"""
        now = datetime.now()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.time_window):
            self.requests.popleft()
        
        # If we've hit the limit, return wait time
        if len(self.requests) >= self.max_requests:
            return (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
        
        return None 