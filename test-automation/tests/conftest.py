"""
Pytest configuration and fixtures for test suite.

Provides pytest-playwright integration and compatibility bridges
for the PyAutoPytest framework.
"""
import os
from types import SimpleNamespace
from typing import Generator, Optional

import pytest
import requests
from playwright.sync_api import Page, BrowserContext

from infra.core.config_manager import get_config
from infra.core.test_context import TestContext
from projects.inspection_portal.facade import InspectionPortalWebFacade
from projects.facility_portal.api_facade import FacilityPortalApiFacade
from projects.inspector_mobile.facade import InspectorMobileFacade


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configure browser context arguments for pytest-playwright.
    
    Sets viewport size and other browser options from config.
    """
    config_manager = get_config()
    
    # Get window size from config (default: 1920x1080)
    window_size = config_manager.get('window_size', '1920x1080')
    width, height = map(int, window_size.split('x'))
    
    return {
        **browser_context_args,
        "viewport": {"width": width, "height": height},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Configure browser launch arguments for pytest-playwright.
    
    Sets headless mode from environment or config.
    """
    config_manager = get_config()
    
    # Check for BROWSER_HEADLESS env var, then config
    headless = os.getenv('BROWSER_HEADLESS', '').lower() in ('true', '1', 'yes')
    if not os.getenv('BROWSER_HEADLESS'):
        headless = config_manager.get('headless', True)  # Default to headless
    
    return {
        **browser_type_launch_args,
        "headless": headless,
    }


@pytest.fixture
def framework_page(page: Page) -> Generator[Page, None, None]:
    """
    Bridge fixture that provides a Playwright Page with framework integration.
    
    This fixture wraps the pytest-playwright 'page' fixture and can be used
    to add framework-specific setup/teardown or context enrichment.
    
    Args:
        page: Playwright Page fixture from pytest-playwright
        
    Yields:
        Page: Playwright Page instance
        
    Usage:
        def test_example(framework_page):
            framework_page.goto("https://example.com")
            framework_page.click("#button")
    """
    # Get configuration
    config_manager = get_config()
    config = config_manager.config
    
    # You can add framework-specific setup here
    # For example, set default timeouts from config
    explicit_wait = config.get('explicit_wait', 30)
    page.set_default_timeout(explicit_wait * 1000)  # Convert to milliseconds
    
    yield page
    
    # Framework-specific teardown can go here
    # For example, capture screenshots on failure (handled by pytest-playwright)


@pytest.fixture
def test_context(framework_page: Page) -> TestContext:
    """
    Create TestContext for backward compatibility with BaseTest pattern.
    
    This fixture provides a TestContext instance that wraps the Playwright Page,
    allowing gradual migration from the old BaseTest pattern.
    
    Args:
        framework_page: Playwright Page with framework integration
        
    Returns:
        TestContext: Framework test context (without driver)
        
    Usage:
        def test_example(test_context):
            base_url = test_context.base_url
            # Use test_context.page for Playwright operations
    """
    config_manager = get_config()
    config = config_manager.config
    
    # Create test context with Page instead of driver
    context = TestContext(
        driver=None,  # No Selenium driver
        base_url=config.get('base_url'),
        config=config
    )
    
    # Attach page for Playwright operations
    context.page = framework_page
    
    return context


@pytest.fixture
def navigate_to(framework_page: Page):
    """
    Helper fixture for navigation relative to base URL.
    
    Args:
        framework_page: Playwright Page with framework integration
        
    Returns:
        Function to navigate to paths relative to base URL
        
    Usage:
        def test_example(navigate_to):
            navigate_to("/login")
            # Navigates to base_url + "/login"
    """
    config_manager = get_config()
    base_url = config_manager.get('base_url', '')
    
    def _navigate_to(path: str = ""):
        """Navigate to URL relative to base URL."""
        if path.startswith('http://') or path.startswith('https://'):
            url = path
        else:
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}" if path else base_url
        framework_page.goto(url)
    
    return _navigate_to


@pytest.fixture(scope="session")
def requests_session() -> Generator[requests.Session, None, None]:
    """
    Provide a requests.Session for API testing.
    
    Yields:
        requests.Session instance
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def appium_driver() -> Optional[object]:
    """
    Provide Appium driver for mobile testing.
    
    This is a placeholder that returns None. 
    TODO: Implement real Appium driver initialization when mobile testing is ready.
    
    Returns:
        None (placeholder for Appium driver)
    """
    # TODO: Initialize and return actual Appium WebDriver
    # from appium import webdriver
    # desired_caps = {...}
    # driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    # yield driver
    # driver.quit()
    
    return None


@pytest.fixture
def config() -> SimpleNamespace:
    """
    Provide configuration namespace for tests.
    
    Returns:
        SimpleNamespace with base_url, api_base_url, and mobile config
    """
    config_manager = get_config()
    
    # Get base URLs from config
    base_url = config_manager.get('base_url', 'https://example.com')
    # API base URL - TODO: Update with actual API URL from config
    api_base_url = config_manager.get('api_base_url', f"{base_url}/api")
    
    # Mobile config - TODO: Update with actual mobile app config
    mobile_config = {
        'platformName': 'Android',
        'platformVersion': '11.0',
        'deviceName': 'emulator',
        'app': '/path/to/app.apk',  # TODO: Update with actual app path
        'automationName': 'UiAutomator2'
    }
    
    return SimpleNamespace(
        base_url=base_url,
        api_base_url=api_base_url,
        mobile=mobile_config
    )


@pytest.fixture(autouse=True)
def attach_facades(
    request,
    page: Page,
    requests_session: requests.Session,
    config: SimpleNamespace,
    appium_driver: Optional[object]
):
    """
    Attach project facades to test class instances.
    
    This fixture automatically attaches web, api, and appium facades to test
    instances, enabling tests to use:
    - self.web.inspection_portal for web UI actions
    - self.api.facility_portal for API actions
    - self.appium.inspector_mobile for mobile actions
    
    Args:
        request: Pytest request object
        page: Playwright Page fixture
        requests_session: Requests Session fixture
        config: Configuration namespace
        appium_driver: Appium driver (placeholder)
    """
    # Only attach to test class instances
    if not hasattr(request, 'instance') or request.instance is None:
        return
    
    # Create web facade namespace
    web = SimpleNamespace(
        inspection_portal=InspectionPortalWebFacade(page, config.base_url)
    )
    
    # Create API facade namespace
    api = SimpleNamespace(
        facility_portal=FacilityPortalApiFacade(requests_session, config.api_base_url)
    )
    
    # Create mobile facade namespace
    appium = SimpleNamespace(
        inspector_mobile=InspectorMobileFacade(appium_driver, config.mobile)
    )
    
    # Attach facades to test instance
    request.instance.web = web
    request.instance.api = api
    request.instance.appium = appium

