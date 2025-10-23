"""
Driver Manager - Thread-safe manager for WebDriver lifecycle.

⚠️ DEPRECATED: This module is deprecated for web UI testing.
Use pytest-playwright fixtures instead (page, context, browser).

For backward compatibility, this module is kept but raises warnings.
New tests should use pytest-playwright's built-in fixtures.

Migration guide:
- Old: driver_manager = DriverManager(config)
- New: Use pytest fixture 'page' from pytest-playwright

Example:
    def test_example(page):
        page.goto("https://example.com")
        page.click("#button")
"""
import warnings
from typing import Optional

from infra.utils.logger import get_logger

logger = get_logger(__name__)

# Deprecation warning message
DEPRECATION_MSG = (
    "DriverManager is deprecated for web UI testing. "
    "Use pytest-playwright fixtures (page, context, browser) instead. "
    "See: https://playwright.dev/python/docs/test-runners"
)


class DriverManager:
    """
    DEPRECATED: Thread-safe WebDriver manager using context manager pattern.
    
    Use pytest-playwright fixtures instead.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize DriverManager.
        
        Args:
            config: Configuration dictionary (deprecated)
        """
        warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        self.config = config or {}
    
    def start_driver(self, browser: Optional[str] = None, **kwargs):
        """
        DEPRECATED: Start a new WebDriver instance.
        
        Raises:
            NotImplementedError: Always raised to guide users to Playwright
        """
        raise NotImplementedError(
            "Selenium WebDriver is no longer supported. "
            "Use pytest-playwright fixtures: def test_example(page): ..."
        )
    
    def get_driver(self):
        """
        DEPRECATED: Get WebDriver instance.
        
        Returns:
            None (deprecated)
        """
        return None
    
    def stop_driver(self) -> None:
        """DEPRECATED: Stop and cleanup WebDriver."""
        pass
    
    def __enter__(self):
        """Context manager entry - deprecated."""
        warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - deprecated."""
        pass


# Module-level singleton instance (deprecated)
_driver_manager: Optional[DriverManager] = None


def get_driver_manager(config: Optional[dict] = None) -> DriverManager:
    """
    DEPRECATED: Get global DriverManager instance.
    
    Use pytest-playwright fixtures instead.
    
    Args:
        config: Configuration dictionary (deprecated)
        
    Returns:
        DriverManager instance (deprecated)
    """
    warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
    global _driver_manager
    if _driver_manager is None:
        _driver_manager = DriverManager(config)
    return _driver_manager


def reset_driver_manager() -> None:
    """DEPRECATED: Reset global DriverManager instance."""
    global _driver_manager
    _driver_manager = None
