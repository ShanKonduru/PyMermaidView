"""
Windows-specific utilities for handling asyncio and subprocess cleanup.
This module addresses common Windows issues with Playwright and asyncio.
"""

import asyncio
import warnings
import sys
from typing import Any, Coroutine


def suppress_windows_asyncio_warnings():
    """Suppress known Windows asyncio warnings that don't affect functionality."""
    if sys.platform == "win32":
        # Filter out the specific Windows asyncio warnings
        warnings.filterwarnings(
            "ignore",
            message="unclosed transport.*",
            category=ResourceWarning,
        )
        # Note: ValueError for pipe operations cannot be filtered via warnings
        # as it's an exception, not a warning. We handle this in the cleanup code instead.


def run_async_with_cleanup(coro: Coroutine) -> Any:
    """
    Run async coroutine with proper cleanup for Windows.
    This helps prevent the unclosed transport warnings.
    """
    if sys.platform == "win32":
        # Use ProactorEventLoop explicitly on Windows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(coro)
        finally:
            # Proper cleanup sequence for Windows
            try:
                # Cancel all tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Close the loop
                loop.close()
            except Exception:
                # Ignore cleanup errors
                pass
    else:
        # Standard asyncio.run for other platforms
        return asyncio.run(coro)


class WindowsSafeAsyncContextManager:
    """
    Context manager that safely handles async context managers on Windows.
    Helps prevent resource warnings when Playwright processes aren't cleaned up properly.
    """
    
    def __init__(self, async_context_manager):
        self.async_context_manager = async_context_manager
        self.resource = None
    
    async def __aenter__(self):
        """Enter the async context manager."""
        self.resource = await self.async_context_manager.__aenter__()
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit with proper cleanup."""
        try:
            result = await self.async_context_manager.__aexit__(exc_type, exc_val, exc_tb)
            
            # Give Windows a moment to clean up processes
            if sys.platform == "win32":
                await asyncio.sleep(0.1)
            
            return result
        except Exception:
            # Don't let cleanup exceptions mask the original exception
            return False


def configure_windows_asyncio():
    """Configure asyncio for better Windows compatibility."""
    if sys.platform == "win32":
        # Suppress warnings
        suppress_windows_asyncio_warnings()
        
        # Set event loop policy for better Windows support
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            # Older Python versions
            pass


# Automatically configure when module is imported
configure_windows_asyncio()