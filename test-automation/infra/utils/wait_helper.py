"""
Wait Helper - Selenium WebDriverWait wrapper utilities.

Provides convenient wrapper functions for common wait operations using
Selenium's expected conditions.
"""
from typing import Any, Callable, Tuple, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from infra.utils.logger import get_logger

logger = get_logger(__name__)

# Type alias for locator tuple
Locator = Tuple[By, str]


def wait_for_element(
    driver: WebDriver,
    locator: Locator,
    timeout: int = 10,
    poll_frequency: float = 0.5
) -> WebElement:
    """
    Wait for element to be present in DOM.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        
    Returns:
        WebElement when found
        
    Raises:
        TimeoutException: If element not found within timeout
    """
    logger.debug(f"Waiting for element: {locator}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(EC.presence_of_element_located(locator))


def wait_for_element_visible(
    driver: WebDriver,
    locator: Locator,
    timeout: int = 10,
    poll_frequency: float = 0.5
) -> WebElement:
    """
    Wait for element to be visible.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        
    Returns:
        WebElement when visible
        
    Raises:
        TimeoutException: If element not visible within timeout
    """
    logger.debug(f"Waiting for element to be visible: {locator}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(EC.visibility_of_element_located(locator))


def wait_for_element_clickable(
    driver: WebDriver,
    locator: Locator,
    timeout: int = 10,
    poll_frequency: float = 0.5
) -> WebElement:
    """
    Wait for element to be clickable.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        
    Returns:
        WebElement when clickable
        
    Raises:
        TimeoutException: If element not clickable within timeout
    """
    logger.debug(f"Waiting for element to be clickable: {locator}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(EC.element_to_be_clickable(locator))


def wait_for_text_in_element(
    driver: WebDriver,
    locator: Locator,
    text: str,
    timeout: int = 10,
    poll_frequency: float = 0.5
) -> bool:
    """
    Wait for specific text to be present in element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        text: Text to wait for
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        
    Returns:
        True when text is present
        
    Raises:
        TimeoutException: If text not present within timeout
    """
    logger.debug(f"Waiting for text '{text}' in element: {locator}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(EC.text_to_be_present_in_element(locator, text))


def wait_for_element_invisible(
    driver: WebDriver,
    locator: Locator,
    timeout: int = 10,
    poll_frequency: float = 0.5
) -> bool:
    """
    Wait for element to become invisible or removed from DOM.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        
    Returns:
        True when element is invisible
        
    Raises:
        TimeoutException: If element still visible after timeout
    """
    logger.debug(f"Waiting for element to be invisible: {locator}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(EC.invisibility_of_element_located(locator))


def wait_for_condition(
    driver: WebDriver,
    condition: Callable[[WebDriver], Any],
    timeout: int = 10,
    poll_frequency: float = 0.5,
    message: str = ""
) -> Any:
    """
    Wait for a custom condition to be met.
    
    Args:
        driver: WebDriver instance
        condition: Callable that takes WebDriver and returns truthy value when condition is met
        timeout: Maximum wait time in seconds
        poll_frequency: Polling interval in seconds
        message: Optional message for TimeoutException
        
    Returns:
        Result of condition function
        
    Raises:
        TimeoutException: If condition not met within timeout
    """
    logger.debug(f"Waiting for custom condition: {message or 'no description'}")
    wait = WebDriverWait(driver, timeout, poll_frequency=poll_frequency)
    return wait.until(condition, message=message)
