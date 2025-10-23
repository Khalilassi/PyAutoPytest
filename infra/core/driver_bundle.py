"""
Driver Bundle for PyAutoPytest Framework
Wraps different driver types (Web, API, Mobile) into a unified interface.
"""
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
import requests


class DriverBundle:
    """
    Bundle class that wraps different driver types.
    Provides unified interface for web, API, and mobile automation.
    """
    
    def __init__(
        self,
        web_driver: Optional[WebDriver] = None,
        api_session: Optional[requests.Session] = None,
        mobile_driver: Optional[AppiumWebDriver] = None
    ):
        """
        Initialize DriverBundle with optional drivers.
        
        Args:
            web_driver: Selenium WebDriver instance
            api_session: Requests Session instance
            mobile_driver: Appium WebDriver instance
        """
        self._web_driver = web_driver
        self._api_session = api_session
        self._mobile_driver = mobile_driver
        self._wait: Optional[WebDriverWait] = None
    
    @property
    def web(self) -> Optional[WebDriver]:
        """
        Get the web driver instance.
        
        Returns:
            Selenium WebDriver instance or None
        """
        return self._web_driver
    
    @property
    def api(self) -> Optional[requests.Session]:
        """
        Get the API session instance.
        
        Returns:
            Requests Session instance or None
        """
        return self._api_session
    
    @property
    def mobile(self) -> Optional[AppiumWebDriver]:
        """
        Get the mobile driver instance.
        
        Returns:
            Appium WebDriver instance or None
        """
        return self._mobile_driver
    
    @property
    def wait(self) -> Optional[WebDriverWait]:
        """
        Get the WebDriverWait instance for web driver.
        
        Returns:
            WebDriverWait instance or None
        """
        return self._wait
    
    def set_web_driver(self, driver: WebDriver, wait_timeout: int = 10) -> None:
        """
        Set the web driver and create WebDriverWait instance.
        
        Args:
            driver: Selenium WebDriver instance
            wait_timeout: Timeout for WebDriverWait in seconds
        """
        self._web_driver = driver
        if driver:
            self._wait = WebDriverWait(driver, wait_timeout)
    
    def set_api_session(self, session: requests.Session) -> None:
        """
        Set the API session.
        
        Args:
            session: Requests Session instance
        """
        self._api_session = session
    
    def set_mobile_driver(self, driver: AppiumWebDriver, wait_timeout: int = 10) -> None:
        """
        Set the mobile driver and create WebDriverWait instance.
        
        Args:
            driver: Appium WebDriver instance
            wait_timeout: Timeout for WebDriverWait in seconds
        """
        self._mobile_driver = driver
        if driver:
            self._wait = WebDriverWait(driver, wait_timeout)
    
    def has_web_driver(self) -> bool:
        """
        Check if web driver is available.
        
        Returns:
            True if web driver exists, False otherwise
        """
        return self._web_driver is not None
    
    def has_api_session(self) -> bool:
        """
        Check if API session is available.
        
        Returns:
            True if API session exists, False otherwise
        """
        return self._api_session is not None
    
    def has_mobile_driver(self) -> bool:
        """
        Check if mobile driver is available.
        
        Returns:
            True if mobile driver exists, False otherwise
        """
        return self._mobile_driver is not None
    
    def quit_all(self) -> None:
        """Quit all drivers and close sessions."""
        if self._web_driver:
            try:
                self._web_driver.quit()
            except Exception:
                pass
            self._web_driver = None
            self._wait = None
        
        if self._mobile_driver:
            try:
                self._mobile_driver.quit()
            except Exception:
                pass
            self._mobile_driver = None
        
        if self._api_session:
            try:
                self._api_session.close()
            except Exception:
                pass
            self._api_session = None
