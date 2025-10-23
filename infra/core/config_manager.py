"""
Configuration Manager for PyAutoPytest Framework
Handles configuration loading and management for test automation.
"""
import os
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages configuration for the test automation framework."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Implement singleton pattern for ConfigManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize ConfigManager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = {}
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration values."""
        self._config = {
            'browser': os.getenv('BROWSER', 'chrome'),
            'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
            'implicit_wait': int(os.getenv('IMPLICIT_WAIT', '10')),
            'explicit_wait': int(os.getenv('EXPLICIT_WAIT', '20')),
            'page_load_timeout': int(os.getenv('PAGE_LOAD_TIMEOUT', '30')),
            'base_url': os.getenv('BASE_URL', 'http://localhost'),
            'api_base_url': os.getenv('API_BASE_URL', 'http://localhost/api'),
            'mobile_platform': os.getenv('MOBILE_PLATFORM', 'android'),
            'appium_server': os.getenv('APPIUM_SERVER', 'http://127.0.0.1:4723'),
            'screenshot_on_failure': os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file (JSON or YAML).
        
        Args:
            file_path: Path to configuration file
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                file_config = yaml.safe_load(f)
            elif path.suffix == '.json':
                file_config = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        # Merge with existing config
        self._config.update(file_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration values
        """
        return self._config.copy()
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with multiple values.
        
        Args:
            config: Dictionary of configuration values to update
        """
        self._config.update(config)
    
    def reset(self) -> None:
        """Reset configuration to default values."""
        self._load_default_config()
