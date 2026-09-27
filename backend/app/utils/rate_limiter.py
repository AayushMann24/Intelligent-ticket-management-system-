"""In-memory rate limiter for API endpoints.

This implementation uses a sliding window approach with in-memory storage.
It is designed for single-process deployments and is NOT suitable for
multi-instance deployments without a shared backend (e.g., Redis).

Thread-safe implementation using asyncio locks.
"""

import time
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from app.config import settings


@dataclass
class RateLimitEntry:
    """Stores request timestamps for a single client."""
    timestamps: list = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class InMemoryRateLimiter:
    """Thread-safe in-memory rate limiter using sliding window algorithm.
    
    Not suitable for distributed/multi-process deployments.
    For production multi-instance deployments, replace with Redis-based implementation.
    """
    
    def __init__(self):
        self._storage: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self._cleanup_lock = asyncio.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Clean up stale entries every 5 minutes
    
    def _get_client_key(self, identifier: str, endpoint: str) -> str:
        """Generate a unique key for client + endpoint combination."""
        return f"{identifier}:{endpoint}"
    
    async def _cleanup_stale_entries(self, window_seconds: int) -> None:
        """Remove entries older than the window to prevent memory growth."""
        now = time.time()
        # Only run cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        async with self._cleanup_lock:
            # Double-check after acquiring lock
            if now - self._last_cleanup < self._cleanup_interval:
                return
            
            cutoff = now - window_seconds
            keys_to_delete = []
            
            for key, entry in self._storage.items():
                async with entry.lock:
                    # Remove timestamps outside the window
                    entry.timestamps = [ts for ts in entry.timestamps if ts > cutoff]
                    if not entry.timestamps:
                        keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._storage[key]
            
            self._last_cleanup = now
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> Tuple[bool, int, int]:
        """Check if request is within rate limit.
        
        Args:
            identifier: Client identifier (e.g., IP address)
            endpoint: Endpoint path (e.g., "/auth/login")
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed: bool, remaining: int, retry_after: int)
            - allowed: True if request is within limit
            - remaining: Number of requests remaining in window
            - retry_after: Seconds until next request allowed (0 if allowed)
        """
        if not settings.rate_limit_enabled:
            return True, max_requests, 0
        
        key = self._get_client_key(identifier, endpoint)
        entry = self._storage[key]
        now = time.time()
        cutoff = now - window_seconds
        
        async with entry.lock:
            # Clean up old timestamps for this entry
            entry.timestamps = [ts for ts in entry.timestamps if ts > cutoff]
            
            current_count = len(entry.timestamps)
            
            if current_count >= max_requests:
                # Rate limited - calculate retry-after
                oldest = entry.timestamps[0] if entry.timestamps else now
                retry_after = int(oldest + window_seconds - now) + 1
                return False, 0, max(retry_after, 1)
            
            # Add current request
            entry.timestamps.append(now)
            remaining = max_requests - current_count - 1
            return True, remaining, 0
    
    async def reset(self, identifier: str, endpoint: str) -> None:
        """Reset rate limit for a specific client and endpoint."""
        key = self._get_client_key(identifier, endpoint)
        if key in self._storage:
            async with self._storage[key].lock:
                self._storage[key].timestamps.clear()
    
    async def reset_all(self) -> None:
        """Reset all rate limits (useful for testing)."""
        self._storage.clear()


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


async def get_client_identifier(request) -> str:
    """Extract client identifier from request.
    
    Uses X-Forwarded-For header if available and trusted, otherwise falls back to client host.
    NOTE: In production behind a trusted proxy, configure the proxy to set X-Forwarded-For
    and only trust it from known proxy IPs. For now, we use client host directly
    as this is a single-process deployment.
    """
    # For single-process deployment, use client host directly
    # X-Forwarded-For is spoofable unless behind a trusted proxy
    client = request.client
    if client:
        return client.host
    return "unknown"