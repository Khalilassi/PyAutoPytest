"""
Base Test class for pytest test cases.

Provides setup and teardown with driver management and test context.
All test classes should inherit from this base class.
"""
from typing import Optional

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from infra.core.config_manager import get_config
from infra.core.driver_manager import DriverManager
from infra.core.test_context import TestContext
from infra.utils.logger import get_logger

logger = get_logger(__name__)


class BaseTest:
    """
    Base test class with driver management and test context setup.
    
    Provides:
    - Automatic driver initialization and cleanup
    - Test context with driver and configuration
    - Easy access to driver via self.driver
    - Configuration via self.context.config
    
    Usage:
        class TestLogin(BaseTest):
            def test_successful_login(self):
                self.driver.get("https://example.com")
                assert "Example" in self.driver.title
    """
    
    # Class-level configuration
    browser: Optional[str] = None
    headless: Optional[bool] = None
    
    def setup_method(self, method):
        """
        Setup before each test method.
        
        Initializes driver manager, creates driver, and sets up test context.
        
        Args:
            method: Test method being executed
        """
        logger.info(f"Setting up test: {method.__name__}")
        
        # Load configuration
        config_manager = get_config()
        config = config_manager.config
        
        # Override config with class-level settings if provided
        if self.browser:
            config['browser'] = self.browser
        if self.headless is not None:
            config['headless'] = self.headless
        
        # Create driver manager and start driver
        self.driver_manager = DriverManager(config)
        self.driver: WebDriver = self.driver_manager.start_driver()
        
        # Create test context
        self.context = TestContext(
            driver=self.driver,
            base_url=config.get('base_url'),
            config=config
        )
        
        logger.info(f"Test setup complete: {method.__name__}")
    
    def teardown_method(self, method):
        """
        Cleanup after each test method.
        
        Stops driver and cleans up resources.
        
        Args:
            method: Test method that was executed
        """
        logger.info(f"Tearing down test: {method.__name__}")
        
        if hasattr(self, 'driver_manager'):
            self.driver_manager.stop_driver()
        
        logger.info(f"Test teardown complete: {method.__name__}")
    
    def get_base_url(self) -> str:
        """
        Get base URL from configuration.
        
        Returns:
            Base URL string
        """
        return self.context.base_url or ""
    
    def navigate_to(self, path: str = "") -> None:
        """
        Navigate to URL relative to base URL.
        
        Args:
            path: Path to append to base URL (can be absolute URL)
        """
        if path.startswith('http://') or path.startswith('https://'):
            url = path
        else:
            base_url = self.get_base_url()
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}" if path else base_url
        
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
