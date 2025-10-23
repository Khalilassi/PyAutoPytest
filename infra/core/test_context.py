"""
Test Context for PyAutoPytest Framework
Provides shared context for test execution and data sharing.
"""
from typing import Any, Dict, Optional
from datetime import datetime
import threading


class TestContext:
    """
    Test context for sharing data across tests and test steps.
    Implements thread-safe singleton pattern.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize TestContext."""
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    self._data: Dict[str, Any] = {}
                    self._metadata: Dict[str, Any] = {}
                    self._test_start_time: Optional[datetime] = None
                    self._test_name: Optional[str] = None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the test context.
        
        Args:
            key: Context key
            value: Context value
        """
        with self._lock:
            self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the test context.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        with self._lock:
            return self._data.get(key, default)
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        
        Args:
            key: Context key
            
        Returns:
            True if key exists, False otherwise
        """
        with self._lock:
            return key in self._data
    
    def remove(self, key: str) -> None:
        """
        Remove a key from the context.
        
        Args:
            key: Context key to remove
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all context data.
        
        Returns:
            Dictionary of all context data
        """
        with self._lock:
            return self._data.copy()
    
    def clear(self) -> None:
        """Clear all context data."""
        with self._lock:
            self._data.clear()
            self._metadata.clear()
            self._test_start_time = None
            self._test_name = None
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        with self._lock:
            self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        with self._lock:
            return self._metadata.get(key, default)
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata.
        
        Returns:
            Dictionary of all metadata
        """
        with self._lock:
            return self._metadata.copy()
    
    def start_test(self, test_name: str) -> None:
        """
        Mark the start of a test.
        
        Args:
            test_name: Name of the test
        """
        with self._lock:
            self._test_name = test_name
            self._test_start_time = datetime.now()
            self._data.clear()
    
    def end_test(self) -> None:
        """Mark the end of a test and calculate duration."""
        with self._lock:
            if self._test_start_time:
                duration = (datetime.now() - self._test_start_time).total_seconds()
                self.set_metadata('test_duration', duration)
            self._test_name = None
            self._test_start_time = None
    
    def get_test_name(self) -> Optional[str]:
        """
        Get the current test name.
        
        Returns:
            Current test name or None
        """
        with self._lock:
            return self._test_name
    
    def get_test_duration(self) -> Optional[float]:
        """
        Get the test duration in seconds.
        
        Returns:
            Test duration in seconds or None
        """
        with self._lock:
            if self._test_start_time:
                return (datetime.now() - self._test_start_time).total_seconds()
            return self.get_metadata('test_duration')
    
    def update(self, data: Dict[str, Any]) -> None:
        """
        Update context with multiple key-value pairs.
        
        Args:
            data: Dictionary of key-value pairs to update
        """
        with self._lock:
            self._data.update(data)
