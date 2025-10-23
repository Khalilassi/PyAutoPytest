"""
Driver Factory for creating Selenium WebDriver instances.

⚠️ DEPRECATED: This module is deprecated for web UI testing.
Use pytest-playwright fixtures instead (page, context, browser).

For backward compatibility, this module is kept but raises warnings.
New tests should use pytest-playwright's built-in fixtures.

Migration guide:
- Old: driver = create_driver()
- New: Use pytest fixture 'page' from pytest-playwright

Example:
    def test_example(page):
        page.goto("https://example.com")
        page.click("#button")
"""
import warnings
from typing import Optional

from infra.utils.logger import get_logger

logger = get_logger(__name__)

# Deprecation warning message
DEPRECATION_MSG = (
    "driver_factory is deprecated for web UI testing. "
    "Use pytest-playwright fixtures (page, context, browser) instead. "
    "See: https://playwright.dev/python/docs/test-runners"
)


def create_chrome_driver(*args, **kwargs):
    """
    DEPRECATED: Use pytest-playwright fixtures instead.
    
    Raises:
        DeprecationWarning: Always raised to guide users to Playwright
    """
    warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
    raise NotImplementedError(
        "Selenium WebDriver is no longer supported. "
        "Use pytest-playwright fixtures: def test_example(page): ..."
    )


def create_firefox_driver(*args, **kwargs):
    """
    DEPRECATED: Use pytest-playwright fixtures instead.
    
    Raises:
        DeprecationWarning: Always raised to guide users to Playwright
    """
    warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
    raise NotImplementedError(
        "Selenium WebDriver is no longer supported. "
        "Use pytest-playwright fixtures: def test_example(page): ..."
    )


def create_driver(*args, **kwargs):
    """
    DEPRECATED: Use pytest-playwright fixtures instead.
    
    Raises:
        DeprecationWarning: Always raised to guide users to Playwright
    """
    warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
    raise NotImplementedError(
        "Selenium WebDriver is no longer supported. "
        "Use pytest-playwright fixtures: def test_example(page): ..."
    )
