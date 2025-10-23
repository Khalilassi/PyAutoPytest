"""
Driver Bundle - Container for WebDriver instance with metadata.

Simple container to hold driver instance along with associated metadata
like browser type, configuration, and timestamps.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class DriverBundle:
    """
    Container for WebDriver instance with metadata.
    
    Attributes:
        driver: Selenium WebDriver instance
        browser: Browser type (chrome, firefox, etc.)
        created_at: Timestamp when driver was created
        config: Configuration dictionary used to create driver
    """
    driver: WebDriver
    browser: str = "chrome"
    created_at: datetime = field(default_factory=datetime.now)
    config: Optional[dict] = None
    
    def quit(self) -> None:
        """Quit the WebDriver and clean up resources."""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures driver is quit."""
        self.quit()
