"""
Web Helper utilities for Selenium interactions.

Provides high-level wrapper functions for common web automation tasks
using Selenium and wait helpers.
"""
from typing import List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from infra.utils.logger import get_logger
from infra.utils.wait_helper import (
    wait_for_element,
    wait_for_element_clickable,
    wait_for_element_visible
)

logger = get_logger(__name__)


def click_element(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10
) -> None:
    """
    Click element after waiting for it to be clickable.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
    """
    logger.debug(f"Clicking element: {locator}")
    element = wait_for_element_clickable(driver, locator, timeout)
    element.click()


def type_text(
    driver: WebDriver,
    locator: Tuple[By, str],
    text: str,
    clear_first: bool = True,
    timeout: int = 10
) -> None:
    """
    Type text into element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        text: Text to type
        clear_first: Clear existing text before typing
        timeout: Maximum wait time in seconds
    """
    logger.debug(f"Typing text into element: {locator}")
    element = wait_for_element_visible(driver, locator, timeout)
    if clear_first:
        element.clear()
    element.send_keys(text)


def get_text(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10
) -> str:
    """
    Get text from element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        
    Returns:
        Element text
    """
    logger.debug(f"Getting text from element: {locator}")
    element = wait_for_element_visible(driver, locator, timeout)
    return element.text


def get_attribute(
    driver: WebDriver,
    locator: Tuple[By, str],
    attribute: str,
    timeout: int = 10
) -> str:
    """
    Get attribute value from element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        attribute: Attribute name
        timeout: Maximum wait time in seconds
        
    Returns:
        Attribute value
    """
    logger.debug(f"Getting attribute '{attribute}' from element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    return element.get_attribute(attribute) or ""


def is_element_visible(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 5
) -> bool:
    """
    Check if element is visible.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        
    Returns:
        True if visible, False otherwise
    """
    try:
        wait_for_element_visible(driver, locator, timeout)
        return True
    except Exception:
        return False


def is_element_present(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 5
) -> bool:
    """
    Check if element is present in DOM.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        
    Returns:
        True if present, False otherwise
    """
    try:
        wait_for_element(driver, locator, timeout)
        return True
    except Exception:
        return False


def select_dropdown_by_text(
    driver: WebDriver,
    locator: Tuple[By, str],
    text: str,
    timeout: int = 10
) -> None:
    """
    Select dropdown option by visible text.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        text: Visible text of option to select
        timeout: Maximum wait time in seconds
    """
    from selenium.webdriver.support.select import Select
    
    logger.debug(f"Selecting dropdown option '{text}' in element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    select = Select(element)
    select.select_by_visible_text(text)


def select_dropdown_by_value(
    driver: WebDriver,
    locator: Tuple[By, str],
    value: str,
    timeout: int = 10
) -> None:
    """
    Select dropdown option by value attribute.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        value: Value attribute of option to select
        timeout: Maximum wait time in seconds
    """
    from selenium.webdriver.support.select import Select
    
    logger.debug(f"Selecting dropdown option with value '{value}' in element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    select = Select(element)
    select.select_by_value(value)


def press_key(
    driver: WebDriver,
    locator: Tuple[By, str],
    key: Keys,
    timeout: int = 10
) -> None:
    """
    Press keyboard key in element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        key: Key to press (from selenium.webdriver.common.keys.Keys)
        timeout: Maximum wait time in seconds
    """
    logger.debug(f"Pressing key {key} in element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    element.send_keys(key)


def wait_for(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10,
    visible: bool = True
) -> WebElement:
    """
    Wait for element with configurable visibility check.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
        visible: Wait for visibility if True, else just presence
        
    Returns:
        WebElement when found
    """
    if visible:
        return wait_for_element_visible(driver, locator, timeout)
    else:
        return wait_for_element(driver, locator, timeout)


def scroll_to_element(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10
) -> None:
    """
    Scroll element into view.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
    """
    logger.debug(f"Scrolling to element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def hover_over_element(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10
) -> None:
    """
    Hover mouse over element.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
    """
    from selenium.webdriver.common.action_chains import ActionChains
    
    logger.debug(f"Hovering over element: {locator}")
    element = wait_for_element(driver, locator, timeout)
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()


def switch_to_frame(
    driver: WebDriver,
    locator: Tuple[By, str],
    timeout: int = 10
) -> None:
    """
    Switch to iframe.
    
    Args:
        driver: WebDriver instance
        locator: Tuple of (By, locator_string)
        timeout: Maximum wait time in seconds
    """
    logger.debug(f"Switching to frame: {locator}")
    element = wait_for_element(driver, locator, timeout)
    driver.switch_to.frame(element)


def switch_to_default_content(driver: WebDriver) -> None:
    """
    Switch back to main content from iframe.
    
    Args:
        driver: WebDriver instance
    """
    logger.debug("Switching to default content")
    driver.switch_to.default_content()
