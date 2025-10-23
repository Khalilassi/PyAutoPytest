"""
Driver Factory for PyAutoPytest Framework
Creates driver instances based on configuration.
"""
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
import requests

from .config_manager import ConfigManager


class DriverFactory:
    """Factory class for creating driver instances."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize DriverFactory.
        
        Args:
            config_manager: ConfigManager instance, creates new one if not provided
        """
        self.config = config_manager or ConfigManager()
    
    def create_web_driver(self, browser: Optional[str] = None, **kwargs) -> webdriver.Remote:
        """
        Create a web driver instance.
        
        Args:
            browser: Browser name (chrome, firefox, edge, safari)
            **kwargs: Additional driver options
            
        Returns:
            Selenium WebDriver instance
        """
        browser = browser or self.config.get('browser', 'chrome')
        browser = browser.lower()
        
        if browser == 'chrome':
            return self._create_chrome_driver(**kwargs)
        elif browser == 'firefox':
            return self._create_firefox_driver(**kwargs)
        elif browser == 'edge':
            return self._create_edge_driver(**kwargs)
        elif browser == 'safari':
            return self._create_safari_driver(**kwargs)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    def _create_chrome_driver(self, **kwargs) -> webdriver.Chrome:
        """Create Chrome WebDriver."""
        options = ChromeOptions()
        
        # Apply headless mode
        if self.config.get('headless', False):
            options.add_argument('--headless=new')
        
        # Common Chrome arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Apply custom options
        if 'options' in kwargs:
            options = kwargs.pop('options')
        
        driver = webdriver.Chrome(options=options, **kwargs)
        self._configure_driver(driver)
        return driver
    
    def _create_firefox_driver(self, **kwargs) -> webdriver.Firefox:
        """Create Firefox WebDriver."""
        options = FirefoxOptions()
        
        # Apply headless mode
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        # Apply custom options
        if 'options' in kwargs:
            options = kwargs.pop('options')
        
        driver = webdriver.Firefox(options=options, **kwargs)
        self._configure_driver(driver)
        return driver
    
    def _create_edge_driver(self, **kwargs) -> webdriver.Edge:
        """Create Edge WebDriver."""
        options = EdgeOptions()
        
        # Apply headless mode
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        # Apply custom options
        if 'options' in kwargs:
            options = kwargs.pop('options')
        
        driver = webdriver.Edge(options=options, **kwargs)
        self._configure_driver(driver)
        return driver
    
    def _create_safari_driver(self, **kwargs) -> webdriver.Safari:
        """Create Safari WebDriver."""
        driver = webdriver.Safari(**kwargs)
        self._configure_driver(driver)
        return driver
    
    def _configure_driver(self, driver: webdriver.Remote) -> None:
        """
        Configure driver with timeouts and other settings.
        
        Args:
            driver: WebDriver instance to configure
        """
        driver.implicitly_wait(self.config.get('implicit_wait', 10))
        driver.set_page_load_timeout(self.config.get('page_load_timeout', 30))
        
        # Maximize window if not headless
        if not self.config.get('headless', False):
            try:
                driver.maximize_window()
            except Exception:
                pass
    
    def create_api_session(self, base_url: Optional[str] = None, **kwargs) -> requests.Session:
        """
        Create an API session.
        
        Args:
            base_url: Base URL for API requests
            **kwargs: Additional session configuration
            
        Returns:
            Requests Session instance
        """
        session = requests.Session()
        
        # Set base URL if provided
        if base_url:
            session.headers.update({'Base-URL': base_url})
        
        # Apply custom headers
        if 'headers' in kwargs:
            session.headers.update(kwargs.pop('headers'))
        
        # Apply other configurations
        for key, value in kwargs.items():
            setattr(session, key, value)
        
        return session
    
    def create_mobile_driver(
        self,
        platform: Optional[str] = None,
        **capabilities
    ) -> appium_webdriver.Remote:
        """
        Create a mobile driver instance.
        
        Args:
            platform: Mobile platform (android, ios)
            **capabilities: Appium capabilities
            
        Returns:
            Appium WebDriver instance
        """
        platform = platform or self.config.get('mobile_platform', 'android')
        platform = platform.lower()
        
        appium_server = self.config.get('appium_server', 'http://127.0.0.1:4723')
        
        if platform == 'android':
            return self._create_android_driver(appium_server, **capabilities)
        elif platform == 'ios':
            return self._create_ios_driver(appium_server, **capabilities)
        else:
            raise ValueError(f"Unsupported mobile platform: {platform}")
    
    def _create_android_driver(
        self,
        appium_server: str,
        **capabilities
    ) -> appium_webdriver.Remote:
        """Create Android driver."""
        options = UiAutomator2Options()
        
        # Set default capabilities
        default_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'Android Emulator',
        }
        
        # Merge with provided capabilities
        default_caps.update(capabilities)
        
        for key, value in default_caps.items():
            options.set_capability(key, value)
        
        driver = appium_webdriver.Remote(
            command_executor=appium_server,
            options=options
        )
        
        driver.implicitly_wait(self.config.get('implicit_wait', 10))
        return driver
    
    def _create_ios_driver(
        self,
        appium_server: str,
        **capabilities
    ) -> appium_webdriver.Remote:
        """Create iOS driver."""
        options = XCUITestOptions()
        
        # Set default capabilities
        default_caps = {
            'platformName': 'iOS',
            'automationName': 'XCUITest',
            'deviceName': 'iPhone Simulator',
        }
        
        # Merge with provided capabilities
        default_caps.update(capabilities)
        
        for key, value in default_caps.items():
            options.set_capability(key, value)
        
        driver = appium_webdriver.Remote(
            command_executor=appium_server,
            options=options
        )
        
        driver.implicitly_wait(self.config.get('implicit_wait', 10))
        return driver
