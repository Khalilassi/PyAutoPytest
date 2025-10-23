"""
PyAutoPytest Core Module
Exposes key classes for test automation framework.
"""

from .config_manager import ConfigManager
from .driver_bundle import DriverBundle
from .driver_factory import DriverFactory
from .driver_manager import DriverManager
from .test_context import TestContext

__all__ = [
    'ConfigManager',
    'DriverBundle',
    'DriverFactory',
    'DriverManager',
    'TestContext',
]

__version__ = '0.1.0'
