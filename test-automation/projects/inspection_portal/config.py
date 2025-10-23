"""
Configuration for Inspection Portal project.

Loads environment-specific configuration using the infrastructure config manager.
"""
from infra.core.config_manager import get_config

# Get global config manager instance
config_manager = get_config()

# Export commonly used config values
BASE_URL = config_manager.get('base_url', 'https://dev.example.com')
BROWSER = config_manager.get('browser', 'chrome')
IMPLICIT_WAIT = config_manager.get('implicit_wait', 10)
EXPLICIT_WAIT = config_manager.get('explicit_wait', 20)
HEADLESS = config_manager.get('headless', False)


def get_project_config(key: str, default=None):
    """
    Get configuration value for inspection portal project.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    return config_manager.get(key, default)
