"""
Base Page Object class for web UI testing.

Provides common page object functionality and element interaction helpers
using Playwright sync API.
"""
from typing import Optional

from playwright.sync_api import Page

from infra.utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Base Page Object class with common element interaction methods using Playwright.
    
    Provides:
    - Element interaction with auto-waiting
    - Common interactions (click, fill, etc.)
    - Page validation helpers
    
    Usage:
        class LoginPage(BasePage):
            USERNAME_INPUT = "#username"
            PASSWORD_INPUT = "#password"
            
            def login(self, username, password):
                self.fill(self.USERNAME_INPUT, username)
                self.fill(self.PASSWORD_INPUT, password)
                self.click(self.LOGIN_BUTTON)
    
    TODO: Update project-specific page objects to use CSS/XPath selectors
    TODO: Replace Selenium By locators with Playwright selector strings
    """
    
    def __init__(self, page: Page):
        """
        Initialize BasePage with Playwright Page instance.
        
        Args:
            page: Playwright sync_api.Page instance
        """
        self.page = page
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def goto(self, path: str, **kwargs) -> None:
        """
        Navigate to URL (absolute or relative to base URL).
        
        Args:
            path: Path to navigate to
            **kwargs: Additional options for page.goto()
        
        TODO: Configure base URL in test context/config for relative paths
        """
        logger.debug(f"Navigating to: {path}")
        self.page.goto(path, **kwargs)
    
    def click(self, selector: str, timeout: int = 10000) -> None:
        """
        Click element using Playwright selector.
        
        Playwright automatically waits for element to be actionable.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            timeout: Maximum wait time in milliseconds (default: 10000)
        """
        logger.debug(f"Clicking element: {selector}")
        self.page.click(selector, timeout=timeout)
    
    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        """
        Fill input element with value.
        
        Playwright automatically waits for element and clears before filling.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            value: Text to fill
            timeout: Maximum wait time in milliseconds (default: 10000)
        """
        logger.debug(f"Filling element: {selector}")  # Don't log the value for security
        self.page.fill(selector, value, timeout=timeout)
    
    def get_text(self, selector: str, timeout: int = 10000) -> str:
        """
        Get text content from element.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            timeout: Maximum wait time in milliseconds (default: 10000)
            
        Returns:
            Element text content
        """
        logger.debug(f"Getting text from element: {selector}")
        return self.page.inner_text(selector, timeout=timeout)
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible on page.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            timeout: Maximum wait time in milliseconds (default: 5000)
            
        Returns:
            True if visible, False otherwise
        """
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = 10000) -> Optional[str]:
        """
        Get attribute value from element.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            attribute: Attribute name
            timeout: Maximum wait time in milliseconds (default: 10000)
            
        Returns:
            Attribute value or None
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {selector}")
        locator = self.page.locator(selector)
        return locator.get_attribute(attribute, timeout=timeout)
    
    def get_page_title(self) -> str:
        """
        Get current page title.
        
        Returns:
            Page title
        """
        return self.page.title()
    
    def get_current_url(self) -> str:
        """
        Get current page URL.
        
        Returns:
            Current URL
        """
        return self.page.url
    
    def wait_for_selector(self, selector: str, timeout: int = 30000, state: str = "visible") -> None:
        """
        Wait for selector to reach specified state.
        
        Args:
            selector: CSS selector, XPath, or other Playwright selector
            timeout: Maximum wait time in milliseconds (default: 30000)
            state: State to wait for: 'attached', 'detached', 'visible', 'hidden'
        """
        logger.debug(f"Waiting for selector: {selector} to be {state}")
        self.page.wait_for_selector(selector, timeout=timeout, state=state)
