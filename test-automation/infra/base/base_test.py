"""
Base Test class for pytest test cases.

⚠️ DEPRECATED: This module is deprecated for web UI testing.
Use pytest-playwright fixtures instead (page, framework_page, navigate_to).

For API tests, this base class is not needed - use fixtures directly.

Migration guide for UI tests:
- Old: class TestLogin(BaseTest):
- New: class TestLogin: (with pytest fixtures)

Example:
    @pytest.mark.ui
    @pytest.mark.web
    class TestLogin:
        def test_example(self, navigate_to, framework_page):
            navigate_to("/login")
            framework_page.click("#button")
"""
import warnings
from typing import Optional

import pytest

from infra.core.config_manager import get_config
from infra.core.test_context import TestContext
from infra.utils.logger import get_logger

logger = get_logger(__name__)

# Deprecation warning message
DEPRECATION_MSG = (
    "BaseTest is deprecated for web UI testing. "
    "Use pytest-playwright fixtures (page, framework_page, navigate_to) instead. "
    "See README.md for migration examples."
)


class BaseTest:
    """
    DEPRECATED: Base test class with driver management and test context setup.
    
    Use pytest-playwright fixtures instead for new tests.
    This class is kept for backward compatibility but will be removed in future versions.
    
    Migration guide:
        # Old approach:
        class TestLogin(BaseTest):
            def test_example(self):
                self.navigate_to("/login")
                self.driver.get("...")
        
        # New approach:
        class TestLogin:
            def test_example(self, navigate_to, framework_page):
                navigate_to("/login")
                framework_page.click("#button")
    """
    
    # Class-level configuration
    browser: Optional[str] = None
    headless: Optional[bool] = None
    
    def setup_method(self, method):
        """
        DEPRECATED: Setup before each test method.
        
        Raises warning about deprecation.
        
        Args:
            method: Test method being executed
        """
        warnings.warn(DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        logger.warning(f"BaseTest is deprecated. Migrate test to use pytest-playwright fixtures: {method.__name__}")
        
        # Minimal setup for backward compatibility
        config_manager = get_config()
        config = config_manager.config
        
        # Create a minimal test context without driver
        self.context = TestContext(
            driver=None,
            base_url=config.get('base_url'),
            config=config
        )
        
        # Set driver to None to trigger errors if used
        self.driver = None
        self.driver_manager = None
    
    def teardown_method(self, method):
        """
        DEPRECATED: Cleanup after each test method.
        
        Args:
            method: Test method that was executed
        """
        pass
    
    def get_base_url(self) -> str:
        """
        Get base URL from configuration.
        
        Returns:
            Base URL string
        """
        return self.context.base_url or ""
    
    def navigate_to(self, path: str = "") -> None:
        """
        DEPRECATED: Navigate to URL relative to base URL.
        
        Raises:
            NotImplementedError: Always raised to guide users to new approach
        """
        raise NotImplementedError(
            "BaseTest.navigate_to() is deprecated. "
            "Use pytest fixtures: def test_example(navigate_to, framework_page): ..."
        )
