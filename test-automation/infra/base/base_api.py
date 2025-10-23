"""
Base API client class for API testing.

Provides wrapper around requests.Session with common HTTP methods
and error handling for API testing.
"""
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from infra.utils.logger import get_logger

logger = get_logger(__name__)


class BaseApi:
    """
    Base API client with requests.Session and common HTTP methods.
    
    Provides:
    - Session management with retry logic
    - Common HTTP methods (GET, POST, PUT, DELETE, PATCH)
    - Automatic JSON handling
    - Configurable base URL and headers
    
    Usage:
        class AuthApi(BaseApi):
            def login(self, username, password):
                return self.post('/auth/login', json={
                    'username': username,
                    'password': password
                })
    """
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retries: int = 3
    ):
        """
        Initialize BaseApi with session configuration.
        
        Args:
            base_url: Base URL for API endpoints
            headers: Default headers for all requests
            timeout: Default timeout for requests in seconds
            retries: Number of retry attempts for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        if headers:
            self.session.headers.update(headers)
        
        logger.debug(f"Initialized {self.__class__.__name__} with base_url: {base_url}")
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.
        
        Args:
            endpoint: API endpoint (can be relative or absolute)
            
        Returns:
            Full URL
        """
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        logger.info(f"GET {url}")
        
        response = self.session.get(
            url,
            params=params,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        logger.info(f"GET {url} - Status: {response.status_code}")
        return response
    
    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform POST request.
        
        Args:
            endpoint: API endpoint
            json: JSON payload
            data: Form data or other payload
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        logger.info(f"POST {url}")
        
        response = self.session.post(
            url,
            json=json,
            data=data,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        logger.info(f"POST {url} - Status: {response.status_code}")
        return response
    
    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform PUT request.
        
        Args:
            endpoint: API endpoint
            json: JSON payload
            data: Form data or other payload
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        logger.info(f"PUT {url}")
        
        response = self.session.put(
            url,
            json=json,
            data=data,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        logger.info(f"PUT {url} - Status: {response.status_code}")
        return response
    
    def delete(
        self,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Perform DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        logger.info(f"DELETE {url}")
        
        response = self.session.delete(
            url,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        logger.info(f"DELETE {url} - Status: {response.status_code}")
        return response
    
    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform PATCH request.
        
        Args:
            endpoint: API endpoint
            json: JSON payload
            data: Form data or other payload
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        logger.info(f"PATCH {url}")
        
        response = self.session.patch(
            url,
            json=json,
            data=data,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        logger.info(f"PATCH {url} - Status: {response.status_code}")
        return response
    
    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()
        logger.debug(f"Closed session for {self.__class__.__name__}")
