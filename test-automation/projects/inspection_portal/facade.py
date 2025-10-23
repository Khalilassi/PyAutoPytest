"""
Web Facade for Inspection Portal.

High-level web interface that encapsulates all page interactions
for the Inspection Portal project.
"""
from typing import Optional

from playwright.sync_api import Page

from projects.inspection_portal.pages.login_page import LoginPage
from projects.inspection_portal.pages.dashboard_page import DashboardPage
from infra.utils.logger import get_logger

logger = get_logger(__name__)


class InspectionPortalWebFacade:
    """
    High-level web facade for Inspection Portal.
    
    Provides simplified methods for test cases, encapsulating all page-level
    interactions and navigation logic.
    
    Usage in tests:
        def test_login(self):
            self.web.inspection_portal.login('user', 'pass')
            assert self.web.inspection_portal.is_logged_in()
    """
    
    def __init__(self, page: Page, base_url: str):
        """
        Initialize InspectionPortalWebFacade.
        
        Args:
            page: Playwright Page instance
            base_url: Base URL for the application (e.g., "https://example.com")
        """
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        logger.info(f"Initialized InspectionPortalWebFacade with base_url: {base_url}")
    
    def login(self, username: str, password: str) -> None:
        """
        Perform complete login flow.
        
        Navigates to login page and performs login with credentials.
        
        Args:
            username: Username for login
            password: Password for login
        """
        logger.info(f"Performing login for user: {username}")
        
        # Navigate to login page
        self.login_page.goto_login(self.base_url)
        
        # Perform login
        self.login_page.login(username, password)
        
        logger.info("Login completed")
    
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.
        
        Returns:
            True if user is logged in (dashboard is visible)
        """
        return self.dashboard_page.is_dashboard_loaded()
