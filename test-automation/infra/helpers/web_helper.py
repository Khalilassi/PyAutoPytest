"""
Web Helper utilities for Playwright interactions.

Provides high-level wrapper functions for common web automation tasks
using Playwright sync API.
"""
from typing import Optional

from playwright.sync_api import Page

from infra.utils.logger import get_logger

logger = get_logger(__name__)


def click_element(page: Page, selector: str, timeout: int = 10000) -> None:
    """
    Click element using Playwright selector.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Clicking element: {selector}")
    page.click(selector, timeout=timeout)


def type_text(page: Page, selector: str, text: str, timeout: int = 10000) -> None:
    """
    Fill text into element (clears existing text first).
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        text: Text to type
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Typing text into element: {selector}")
    page.fill(selector, text, timeout=timeout)


def get_text(page: Page, selector: str, timeout: int = 10000) -> str:
    """
    Get text from element.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
        
    Returns:
        Element text
    """
    logger.debug(f"Getting text from element: {selector}")
    return page.inner_text(selector, timeout=timeout)


def get_attribute(page: Page, selector: str, attribute: str, timeout: int = 10000) -> str:
    """
    Get attribute value from element.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        attribute: Attribute name
        timeout: Maximum wait time in milliseconds (default: 10000)
        
    Returns:
        Attribute value or empty string
    """
    logger.debug(f"Getting attribute '{attribute}' from element: {selector}")
    locator = page.locator(selector)
    return locator.get_attribute(attribute, timeout=timeout) or ""


def is_element_visible(page: Page, selector: str, timeout: int = 5000) -> bool:
    """
    Check if element is visible.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 5000)
        
    Returns:
        True if visible, False otherwise
    """
    try:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        return True
    except Exception:
        return False


def wait_for(page: Page, selector: str, timeout: int = 10000, state: str = "visible") -> None:
    """
    Wait for element to reach specified state.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
        state: State to wait for: 'attached', 'detached', 'visible', 'hidden'
    """
    logger.debug(f"Waiting for element: {selector} to be {state}")
    page.wait_for_selector(selector, state=state, timeout=timeout)


def get_element(page: Page, selector: str, timeout: int = 10000):
    """
    Get Playwright Locator for element.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
        
    Returns:
        Playwright Locator object
    """
    logger.debug(f"Getting element: {selector}")
    locator = page.locator(selector)
    # Wait for element to be attached
    locator.wait_for(state="attached", timeout=timeout)
    return locator


def select_dropdown_by_text(page: Page, selector: str, text: str, timeout: int = 10000) -> None:
    """
    Select dropdown option by visible text.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector for the select element
        text: Visible text of option to select
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Selecting dropdown option '{text}' in element: {selector}")
    page.select_option(selector, label=text, timeout=timeout)


def select_dropdown_by_value(page: Page, selector: str, value: str, timeout: int = 10000) -> None:
    """
    Select dropdown option by value attribute.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector for the select element
        value: Value attribute of option to select
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Selecting dropdown option with value '{value}' in element: {selector}")
    page.select_option(selector, value=value, timeout=timeout)


def press_key(page: Page, selector: str, key: str, timeout: int = 10000) -> None:
    """
    Press keyboard key in element.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        key: Key to press (e.g., 'Enter', 'Escape', 'ArrowDown')
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Pressing key {key} in element: {selector}")
    locator = page.locator(selector)
    locator.press(key, timeout=timeout)


def scroll_to_element(page: Page, selector: str, timeout: int = 10000) -> None:
    """
    Scroll element into view.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Scrolling to element: {selector}")
    locator = page.locator(selector)
    locator.scroll_into_view_if_needed(timeout=timeout)


def hover_over_element(page: Page, selector: str, timeout: int = 10000) -> None:
    """
    Hover mouse over element.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector, XPath, or other Playwright selector
        timeout: Maximum wait time in milliseconds (default: 10000)
    """
    logger.debug(f"Hovering over element: {selector}")
    page.hover(selector, timeout=timeout)


def switch_to_frame(page: Page, selector: str) -> "Page":
    """
    Get frame object by selector.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector for the iframe element
        
    Returns:
        Frame object (which has the same API as Page)
        
    Note: With Playwright, you can also use page.frame_locator() for more modern approach
    """
    logger.debug(f"Switching to frame: {selector}")
    frame_element = page.locator(selector).element_handle()
    return frame_element.content_frame()
