"""
Logger utility for consistent logging across the framework.

Provides configured logger instances with console output and formatting.
"""
import logging
import sys
from typing import Optional


def get_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a configured logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        
    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        formatter = logging.Formatter(format_string)
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger


def configure_root_logger(level: int = logging.INFO) -> None:
    """
    Configure root logger for the entire framework.
    
    Args:
        level: Logging level for root logger
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
