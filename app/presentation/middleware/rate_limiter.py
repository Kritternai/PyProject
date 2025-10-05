"""
Rate limiting middleware for DoS protection.
Implements rate limiting per user and per IP address.
"""

import time
from functools import wraps
from flask import request, jsonify, g, session
from typing import Dict, Tuple, Optional
from collections import defaultdict, deque
import threading


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm.
    Tracks requests per user and per IP address.
    """
    
    def __init__(self):
        """Initialize rate limiter with thread-safe storage."""
        self._user_requests: Dict[str, deque] = defaultdict(deque)
        self._ip_requests: Dict[str, deque] = defaultdict(deque)
        self._lock = threading.RLock()
    
    def is_allowed(self, identifier: str, limit: int, window: int, storage: Dict[str, deque]) -> Tuple[bool, int]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: User ID or IP address
            limit: Maximum requests allowed
            window: Time window in seconds
            storage: Storage dictionary for requests
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        with self._lock:
            current_time = time.time()
            requests = storage[identifier]
            
            # Remove old requests outside the window
            while requests and requests[0] <= current_time - window:
                requests.popleft()
            
            # Check if limit exceeded
            if len(requests) >= limit:
                return False, 0
            
            # Add current request
            requests.append(current_time)
            remaining = limit - len(requests)
            
            return True, remaining
    
    def check_user_limit(self, user_id: str, limit: int = 10, window: int = 5) -> Tuple[bool, int]:
        """
        Check rate limit for authenticated user.
        
        Args:
            user_id: User identifier
            limit: Maximum requests (default: 10)
            window: Time window in seconds (default: 5)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        return self.is_allowed(user_id, limit, window, self._user_requests)
    
    def check_ip_limit(self, ip_address: str, limit: int = 20, window: int = 5) -> Tuple[bool, int]:
        """
        Check rate limit for IP address.
        
        Args:
            ip_address: Client IP address
            limit: Maximum requests (default: 20)
            window: Time window in seconds (default: 5)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        return self.is_allowed(ip_address, limit, window, self._ip_requests)
    
    def cleanup_old_entries(self, max_age: int = 3600):
        """
        Clean up old entries to prevent memory leaks.
        
        Args:
            max_age: Maximum age of entries in seconds (default: 1 hour)
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - max_age
            
            # Clean user requests
            for user_id in list(self._user_requests.keys()):
                requests = self._user_requests[user_id]
                while requests and requests[0] <= cutoff_time:
                    requests.popleft()
                if not requests:
                    del self._user_requests[user_id]
            
            # Clean IP requests
            for ip in list(self._ip_requests.keys()):
                requests = self._ip_requests[ip]
                while requests and requests[0] <= cutoff_time:
                    requests.popleft()
                if not requests:
                    del self._ip_requests[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip() -> str:
    """
    Get client IP address, considering proxy headers.
    
    Returns:
        Client IP address
    """
    # Check for forwarded IP (behind proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'


def rate_limit(user_limit: int = 10, ip_limit: int = 20, window: int = 5):
    """
    Decorator for rate limiting endpoints.
    
    Args:
        user_limit: Maximum requests per user (default: 10)
        ip_limit: Maximum requests per IP (default: 20)
        window: Time window in seconds (default: 5)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_client_ip()
            user_id = session.get('user_id')
            
            # Check IP-based rate limit (always applied)
            ip_allowed, ip_remaining = rate_limiter.check_ip_limit(client_ip, ip_limit, window)
            
            if not ip_allowed:
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded. Too many requests from your IP address.',
                    'error_code': 'RATE_LIMIT_EXCEEDED_IP',
                    'retry_after': window
                }), 429
            
            # Check user-based rate limit (if authenticated)
            if user_id:
                user_allowed, user_remaining = rate_limiter.check_user_limit(user_id, user_limit, window)
                
                if not user_allowed:
                    return jsonify({
                        'success': False,
                        'message': 'Rate limit exceeded. Too many requests from your account.',
                        'error_code': 'RATE_LIMIT_EXCEEDED_USER',
                        'retry_after': window
                    }), 429
                
                # Add rate limit headers for authenticated users
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit-User'] = str(user_limit)
                    response.headers['X-RateLimit-Remaining-User'] = str(user_remaining)
                    response.headers['X-RateLimit-Window'] = str(window)
                return response
            
            # Add rate limit headers for IP-based limiting
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit-IP'] = str(ip_limit)
                response.headers['X-RateLimit-Remaining-IP'] = str(ip_remaining)
                response.headers['X-RateLimit-Window'] = str(window)
            
            return response
        
        return decorated_function
    return decorator


def strict_rate_limit(user_limit: int = 5, ip_limit: int = 10, window: int = 5):
    """
    Strict rate limiting decorator for sensitive endpoints.
    
    Args:
        user_limit: Maximum requests per user (default: 5)
        ip_limit: Maximum requests per IP (default: 10)
        window: Time window in seconds (default: 5)
    """
    return rate_limit(user_limit, ip_limit, window)


def cleanup_rate_limiter():
    """
    Cleanup function to be called periodically.
    Should be called from a background task or cron job.
    """
    rate_limiter.cleanup_old_entries()
