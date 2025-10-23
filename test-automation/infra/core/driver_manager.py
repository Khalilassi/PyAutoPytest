"""
Driver Manager - Thread-safe manager for WebDriver lifecycle.

Provides singleton/context manager pattern for managing WebDriver instances
with proper cleanup and thread safety.
"""
import threading
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from infra.core.driver_bundle import DriverBundle
from infra.core.driver_factory import create_driver
from infra.utils.logger import get_logger

logger = get_logger(__name__)


class DriverManager:
    """
    Thread-safe WebDriver manager using context manager pattern.
    
    Manages driver lifecycle with proper initialization and cleanup.
    Thread-local storage ensures each thread gets its own driver instance.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize DriverManager.
        
        Args:
            config: Configuration dictionary for driver creation
        """
        self.config = config or {}
        self._local = threading.local()
        self._lock = threading.Lock()
    
    def start_driver(self, browser: Optional[str] = None, **kwargs) -> WebDriver:
        """
        Start a new WebDriver instance for the current thread.
        
        Args:
            browser: Browser type (overrides config)
            **kwargs: Additional arguments for driver creation
            
        Returns:
            WebDriver instance
        """
        with self._lock:
            if hasattr(self._local, 'driver_bundle') and self._local.driver_bundle:
                logger.warning("Driver already exists for this thread, returning existing driver")
                return self._local.driver_bundle.driver
            
            browser = browser or self.config.get('browser', 'chrome')
            logger.info(f"Starting {browser} driver for thread {threading.current_thread().name}")
            
            driver = create_driver(
                browser=browser,
                config=self.config,
                **kwargs
            )
            
            self._local.driver_bundle = DriverBundle(
                driver=driver,
                browser=browser,
                config=self.config
            )
            
            return driver
    
    def get_driver(self) -> Optional[WebDriver]:
        """
        Get WebDriver instance for current thread.
        
        Returns:
            WebDriver instance or None if not started
        """
        if hasattr(self._local, 'driver_bundle') and self._local.driver_bundle:
            return self._local.driver_bundle.driver
        return None
    
    def stop_driver(self) -> None:
        """Stop and cleanup WebDriver for current thread."""
        with self._lock:
            if hasattr(self._local, 'driver_bundle') and self._local.driver_bundle:
                logger.info(f"Stopping driver for thread {threading.current_thread().name}")
                self._local.driver_bundle.quit()
                self._local.driver_bundle = None
    
    def __enter__(self):
        """Context manager entry - starts driver."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stops driver."""
        self.stop_driver()


# Module-level singleton instance
_driver_manager: Optional[DriverManager] = None
_manager_lock = threading.Lock()


def get_driver_manager(config: Optional[dict] = None) -> DriverManager:
    """
    Get global DriverManager instance (singleton pattern).
    
    Args:
        config: Configuration dictionary (used only on first call)
        
    Returns:
        DriverManager instance
    """
    global _driver_manager
    
    if _driver_manager is None:
        with _manager_lock:
            if _driver_manager is None:
                _driver_manager = DriverManager(config)
    
    return _driver_manager


def reset_driver_manager() -> None:
    """Reset global DriverManager instance (useful for testing)."""
    global _driver_manager
    with _manager_lock:
        if _driver_manager:
            _driver_manager.stop_driver()
        _driver_manager = None
