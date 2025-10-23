"""
Base Page Object class for web UI testing.

Provides common page object functionality and element interaction helpers
using Selenium WebDriver.
"""
from typing import List, Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from infra.utils.logger import get_logger
from infra.utils.wait_helper import (
    wait_for_element,
    wait_for_element_clickable,
    wait_for_element_visible
)

logger = get_logger(__name__)


class BasePage:
    """
    Base Page Object class with common element interaction methods.
    
    Provides:
    - Element finding with explicit waits
    - Common interactions (click, type, etc.)
    - Page validation helpers
    
    Usage:
        class LoginPage(BasePage):
            USERNAME_INPUT = (By.ID, "username")
            PASSWORD_INPUT = (By.ID, "password")
            
            def login(self, username, password):
                self.type_text(self.USERNAME_INPUT, username)
                self.type_text(self.PASSWORD_INPUT, password)
                self.click(self.LOGIN_BUTTON)
    """
    
    def __init__(self, driver: WebDriver):
        """
        Initialize BasePage with WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def find_element(
        self,
        locator: Tuple[By, str],
        timeout: int = 10
    ) -> WebElement:
        """
        Find element with explicit wait.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement when found
        """
        logger.debug(f"Finding element: {locator}")
        return wait_for_element(self.driver, locator, timeout)
    
    def find_elements(
        self,
        locator: Tuple[By, str],
        timeout: int = 10
    ) -> List[WebElement]:
        """
        Find multiple elements with explicit wait.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements
        """
        logger.debug(f"Finding elements: {locator}")
        # Wait for at least one element to be present
        wait_for_element(self.driver, locator, timeout)
        return self.driver.find_elements(*locator)
    
    def click(self, locator: Tuple[By, str], timeout: int = 10) -> None:
        """
        Click element after waiting for it to be clickable.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
        """
        logger.debug(f"Clicking element: {locator}")
        element = wait_for_element_clickable(self.driver, locator, timeout)
        element.click()
    
    def type_text(
        self,
        locator: Tuple[By, str],
        text: str,
        clear_first: bool = True,
        timeout: int = 10
    ) -> None:
        """
        Type text into element after waiting for it to be visible.
        
        Args:
            locator: Tuple of (By, locator_string)
            text: Text to type
            clear_first: Clear existing text before typing
            timeout: Maximum wait time in seconds
        """
        logger.debug(f"Typing text into element: {locator}")
        element = wait_for_element_visible(self.driver, locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
    
    def get_text(
        self,
        locator: Tuple[By, str],
        timeout: int = 10
    ) -> str:
        """
        Get text from element.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
            
        Returns:
            Element text
        """
        logger.debug(f"Getting text from element: {locator}")
        element = wait_for_element_visible(self.driver, locator, timeout)
        return element.text
    
    def get_attribute(
        self,
        locator: Tuple[By, str],
        attribute: str,
        timeout: int = 10
    ) -> Optional[str]:
        """
        Get attribute value from element.
        
        Args:
            locator: Tuple of (By, locator_string)
            attribute: Attribute name
            timeout: Maximum wait time in seconds
            
        Returns:
            Attribute value or None
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {locator}")
        element = wait_for_element(self.driver, locator, timeout)
        return element.get_attribute(attribute)
    
    def is_element_visible(
        self,
        locator: Tuple[By, str],
        timeout: int = 5
    ) -> bool:
        """
        Check if element is visible on page.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
            
        Returns:
            True if visible, False otherwise
        """
        try:
            wait_for_element_visible(self.driver, locator, timeout)
            return True
        except Exception:
            return False
    
    def is_element_present(
        self,
        locator: Tuple[By, str],
        timeout: int = 5
    ) -> bool:
        """
        Check if element is present in DOM.
        
        Args:
            locator: Tuple of (By, locator_string)
            timeout: Maximum wait time in seconds
            
        Returns:
            True if present, False otherwise
        """
        try:
            wait_for_element(self.driver, locator, timeout)
            return True
        except Exception:
            return False
    
    def get_page_title(self) -> str:
        """
        Get current page title.
        
        Returns:
            Page title
        """
        return self.driver.title
    
    def get_current_url(self) -> str:
        """
        Get current page URL.
        
        Returns:
            Current URL
        """
        return self.driver.current_url
    
    def wait_for_page_load(self, timeout: int = 30) -> None:
        """
        Wait for page to finish loading.
        
        Args:
            timeout: Maximum wait time in seconds
        """
        from selenium.webdriver.support.ui import WebDriverWait
        
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.debug("Page load complete")
