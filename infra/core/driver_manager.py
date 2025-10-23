"""
Driver Manager for PyAutoPytest Framework
Manages driver lifecycle and provides access to driver bundles.
"""
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from .driver_factory import DriverFactory
from .driver_bundle import DriverBundle
from .config_manager import ConfigManager


logger = logging.getLogger(__name__)


class DriverManager:
    """
    Manages driver instances and their lifecycle.
    Implements singleton pattern to ensure single instance per test session.
    """
    
    _instance = None
    _driver_bundle: Optional[DriverBundle] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize DriverManager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.config = ConfigManager()
            self.factory = DriverFactory(self.config)
            self._driver_bundle = None
            self._screenshot_dir = Path('screenshots')
    
    def get_driver_bundle(self) -> DriverBundle:
        """
        Get the current driver bundle.
        Creates a new one if it doesn't exist.
        
        Returns:
            DriverBundle instance
        """
        if self._driver_bundle is None:
            self._driver_bundle = DriverBundle()
        return self._driver_bundle
    
    def create_web_driver(
        self,
        browser: Optional[str] = None,
        **kwargs
    ) -> DriverBundle:
        """
        Create a web driver and add it to the driver bundle.
        
        Args:
            browser: Browser name
            **kwargs: Additional driver options
            
        Returns:
            DriverBundle with web driver
        """
        if self._driver_bundle is None:
            self._driver_bundle = DriverBundle()
        
        try:
            driver = self.factory.create_web_driver(browser, **kwargs)
            wait_timeout = self.config.get('explicit_wait', 20)
            self._driver_bundle.set_web_driver(driver, wait_timeout)
            logger.info(f"Web driver created successfully: {browser or self.config.get('browser')}")
        except Exception as e:
            logger.error(f"Failed to create web driver: {e}")
            raise
        
        return self._driver_bundle
    
    def create_api_session(
        self,
        base_url: Optional[str] = None,
        **kwargs
    ) -> DriverBundle:
        """
        Create an API session and add it to the driver bundle.
        
        Args:
            base_url: Base URL for API requests
            **kwargs: Additional session configuration
            
        Returns:
            DriverBundle with API session
        """
        if self._driver_bundle is None:
            self._driver_bundle = DriverBundle()
        
        try:
            base_url = base_url or self.config.get('api_base_url')
            session = self.factory.create_api_session(base_url, **kwargs)
            self._driver_bundle.set_api_session(session)
            logger.info(f"API session created successfully: {base_url}")
        except Exception as e:
            logger.error(f"Failed to create API session: {e}")
            raise
        
        return self._driver_bundle
    
    def create_mobile_driver(
        self,
        platform: Optional[str] = None,
        **capabilities
    ) -> DriverBundle:
        """
        Create a mobile driver and add it to the driver bundle.
        
        Args:
            platform: Mobile platform (android, ios)
            **capabilities: Appium capabilities
            
        Returns:
            DriverBundle with mobile driver
        """
        if self._driver_bundle is None:
            self._driver_bundle = DriverBundle()
        
        try:
            driver = self.factory.create_mobile_driver(platform, **capabilities)
            wait_timeout = self.config.get('explicit_wait', 20)
            self._driver_bundle.set_mobile_driver(driver, wait_timeout)
            logger.info(f"Mobile driver created successfully: {platform or self.config.get('mobile_platform')}")
        except Exception as e:
            logger.error(f"Failed to create mobile driver: {e}")
            raise
        
        return self._driver_bundle
    
    def quit_drivers(self) -> None:
        """Quit all drivers and clean up resources."""
        if self._driver_bundle:
            self._driver_bundle.quit_all()
            logger.info("All drivers quit successfully")
    
    def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """
        Take a screenshot with the current driver.
        
        Args:
            name: Base name for the screenshot file
            
        Returns:
            Path to the screenshot file or None
        """
        driver = None
        
        if self._driver_bundle:
            if self._driver_bundle.has_web_driver():
                driver = self._driver_bundle.web
            elif self._driver_bundle.has_mobile_driver():
                driver = self._driver_bundle.mobile
        
        if driver is None:
            logger.warning("No driver available for screenshot")
            return None
        
        try:
            # Create screenshot directory if it doesn't exist
            self._screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self._screenshot_dir / filename
            
            # Take screenshot
            driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def reset(self) -> None:
        """Reset the driver manager by quitting all drivers."""
        self.quit_drivers()
        self._driver_bundle = None
    
    def set_screenshot_directory(self, directory: str) -> None:
        """
        Set the directory for saving screenshots.
        
        Args:
            directory: Path to screenshot directory
        """
        self._screenshot_dir = Path(directory)
