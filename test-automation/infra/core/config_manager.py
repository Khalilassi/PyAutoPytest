"""
Configuration Manager for loading YAML environment configurations.

Handles loading environment-specific configuration files and provides
access to configuration values with defaults.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigManager:
    """
    Manages configuration loading from YAML files based on environment.
    
    Supports environment selection via ENV environment variable or .env file.
    Configuration files are expected in infra/config/{env}.yaml format.
    """
    
    def __init__(self):
        """Initialize ConfigManager and load environment variables."""
        load_dotenv()
        self._config: Dict[str, Any] = {}
        self._env: str = os.getenv('ENV', 'dev')
        self._config_dir = Path(__file__).parent.parent / 'config'
        self.load_env(self._env)
    
    def load_env(self, env: str) -> None:
        """
        Load configuration for the specified environment.
        
        Args:
            env: Environment name (e.g., 'dev', 'staging', 'prod')
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        config_file = self._config_dir / f"{env}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f) or {}
        
        self._env = env
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with optional default.
        
        Supports environment variable overrides for specific keys:
        - BROWSER_HEADLESS: Override headless setting
        - BASE_URL: Override base URL
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check for environment variable overrides
        if key == 'headless' and os.getenv('BROWSER_HEADLESS'):
            return os.getenv('BROWSER_HEADLESS', '').lower() in ('true', '1', 'yes')
        if key == 'base_url' and os.getenv('BASE_URL'):
            return os.getenv('BASE_URL')
        
        # Support dot notation for nested keys
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def env(self) -> str:
        """Get current environment name."""
        return self._env
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config.copy()


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get global ConfigManager instance (singleton pattern).
    
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config() -> None:
    """Reset global ConfigManager instance (useful for testing)."""
    global _config_manager
    _config_manager = None
