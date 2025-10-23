"""
Driver Factory for creating Selenium WebDriver instances.

Provides factory functions to create WebDriver instances for different browsers
using webdriver-manager for automatic driver management.
"""
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from infra.utils.logger import get_logger

logger = get_logger(__name__)


def create_chrome_driver(
    headless: bool = False,
    window_size: str = "1920x1080",
    implicit_wait: int = 10,
    **kwargs
) -> WebDriver:
    """
    Create a Chrome WebDriver instance.
    
    Args:
        headless: Run browser in headless mode
        window_size: Browser window size (e.g., "1920x1080")
        implicit_wait: Implicit wait timeout in seconds
        **kwargs: Additional options to pass to Chrome
        
    Returns:
        Chrome WebDriver instance
    """
    options = ChromeOptions()
    
    if headless:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    
    options.add_argument(f'--window-size={window_size}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Apply any additional options
    for key, value in kwargs.items():
        if isinstance(value, bool) and value:
            options.add_argument(f'--{key}')
        elif value is not None:
            options.add_argument(f'--{key}={value}')
    
    logger.info(f"Creating Chrome driver (headless={headless})")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(implicit_wait)
    
    return driver


def create_firefox_driver(
    headless: bool = False,
    window_size: str = "1920x1080",
    implicit_wait: int = 10,
    **kwargs
) -> WebDriver:
    """
    Create a Firefox WebDriver instance.
    
    Args:
        headless: Run browser in headless mode
        window_size: Browser window size (e.g., "1920x1080")
        implicit_wait: Implicit wait timeout in seconds
        **kwargs: Additional options to pass to Firefox
        
    Returns:
        Firefox WebDriver instance
    """
    options = FirefoxOptions()
    
    if headless:
        options.add_argument('--headless')
    
    # Set window size
    width, height = window_size.split('x')
    
    logger.info(f"Creating Firefox driver (headless={headless})")
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(implicit_wait)
    driver.set_window_size(int(width), int(height))
    
    return driver


def create_driver(
    browser: str = "chrome",
    headless: Optional[bool] = None,
    window_size: Optional[str] = None,
    implicit_wait: Optional[int] = None,
    config: Optional[dict] = None
) -> WebDriver:
    """
    Create a WebDriver instance based on browser type.
    
    Uses configuration values if provided, otherwise uses defaults.
    
    Args:
        browser: Browser type ('chrome' or 'firefox')
        headless: Run browser in headless mode
        window_size: Browser window size
        implicit_wait: Implicit wait timeout
        config: Configuration dictionary to use for defaults
        
    Returns:
        WebDriver instance
        
    Raises:
        ValueError: If browser type is not supported
    """
    # Use config values as defaults if provided
    if config:
        browser = browser or config.get('browser', 'chrome')
        headless = headless if headless is not None else config.get('headless', False)
        window_size = window_size or config.get('window_size', '1920x1080')
        implicit_wait = implicit_wait if implicit_wait is not None else config.get('implicit_wait', 10)
    else:
        headless = headless if headless is not None else False
        window_size = window_size or '1920x1080'
        implicit_wait = implicit_wait if implicit_wait is not None else 10
    
    browser = browser.lower()
    
    if browser == 'chrome':
        return create_chrome_driver(
            headless=headless,
            window_size=window_size,
            implicit_wait=implicit_wait
        )
    elif browser == 'firefox':
        return create_firefox_driver(
            headless=headless,
            window_size=window_size,
            implicit_wait=implicit_wait
        )
    else:
        raise ValueError(f"Unsupported browser type: {browser}. Supported: chrome, firefox")
