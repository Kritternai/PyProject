"""
Background cleanup task for rate limiter.
Prevents memory leaks by cleaning up old rate limiting data.
"""

import threading
import time
from ..presentation.middleware.rate_limiter import cleanup_rate_limiter


class RateLimiterCleanupTask:
    """
    Background task to clean up old rate limiting data.
    Runs in a separate thread to prevent memory leaks.
    """
    
    def __init__(self, cleanup_interval: int = 3600):
        """
        Initialize cleanup task.
        
        Args:
            cleanup_interval: Cleanup interval in seconds (default: 1 hour)
        """
        self.cleanup_interval = cleanup_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the cleanup task."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the cleanup task."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _cleanup_loop(self):
        """Main cleanup loop."""
        while self.running:
            try:
                cleanup_rate_limiter()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                # Log error but continue running
                print(f"Rate limiter cleanup error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


# Global cleanup task instance
cleanup_task = RateLimiterCleanupTask()


def start_cleanup_task():
    """Start the rate limiter cleanup task."""
    cleanup_task.start()


def stop_cleanup_task():
    """Stop the rate limiter cleanup task."""
    cleanup_task.stop()
