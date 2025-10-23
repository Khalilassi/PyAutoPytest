"""
Test Context - Data container for test execution context.

Holds driver, configuration, and other context information needed during test execution.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class TestContext:
    """
    Container for test execution context.
    
    Provides centralized access to driver, configuration, and base URL
    for use across test lifecycle.
    
    Attributes:
        driver: Selenium WebDriver instance
        base_url: Base URL for the application under test
        config: Configuration dictionary
    """
    driver: Optional[WebDriver] = None
    base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self.config:
            return self.config.get(key, default)
        return default
