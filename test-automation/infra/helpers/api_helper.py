"""
API Helper utilities for HTTP requests.

Provides wrapper functions for common API testing operations using requests library
with error handling and logging.
"""
from typing import Any, Dict, Optional

import requests

from infra.utils.logger import get_logger

logger = get_logger(__name__)


def send_get_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    verify_ssl: bool = True
) -> requests.Response:
    """
    Send GET request with error handling.
    
    Args:
        url: Request URL
        params: Query parameters
        headers: Request headers
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: On request failure
    """
    logger.info(f"GET {url}")
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        logger.info(f"GET {url} - Status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"GET {url} failed: {str(e)}")
        raise


def send_post_request(
    url: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    verify_ssl: bool = True
) -> requests.Response:
    """
    Send POST request with error handling.
    
    Args:
        url: Request URL
        json: JSON payload
        data: Form data or other payload
        headers: Request headers
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: On request failure
    """
    logger.info(f"POST {url}")
    
    try:
        response = requests.post(
            url,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        logger.info(f"POST {url} - Status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"POST {url} failed: {str(e)}")
        raise


def send_put_request(
    url: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    verify_ssl: bool = True
) -> requests.Response:
    """
    Send PUT request with error handling.
    
    Args:
        url: Request URL
        json: JSON payload
        data: Form data or other payload
        headers: Request headers
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: On request failure
    """
    logger.info(f"PUT {url}")
    
    try:
        response = requests.put(
            url,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        logger.info(f"PUT {url} - Status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"PUT {url} failed: {str(e)}")
        raise


def send_delete_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    verify_ssl: bool = True
) -> requests.Response:
    """
    Send DELETE request with error handling.
    
    Args:
        url: Request URL
        headers: Request headers
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: On request failure
    """
    logger.info(f"DELETE {url}")
    
    try:
        response = requests.delete(
            url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        logger.info(f"DELETE {url} - Status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"DELETE {url} failed: {str(e)}")
        raise


def parse_json_response(response: requests.Response) -> Dict[str, Any]:
    """
    Parse JSON from response with error handling.
    
    Args:
        response: Response object
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If response is not valid JSON
    """
    try:
        return response.json()
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        logger.error(f"Response content: {response.text[:500]}")
        raise


def validate_response_status(
    response: requests.Response,
    expected_status: int = 200
) -> bool:
    """
    Validate response has expected status code.
    
    Args:
        response: Response object
        expected_status: Expected status code
        
    Returns:
        True if status matches, False otherwise
    """
    is_valid = response.status_code == expected_status
    
    if not is_valid:
        logger.warning(
            f"Status mismatch: expected {expected_status}, got {response.status_code}"
        )
    
    return is_valid


def assert_response_status(
    response: requests.Response,
    expected_status: int = 200
) -> None:
    """
    Assert response has expected status code.
    
    Args:
        response: Response object
        expected_status: Expected status code
        
    Raises:
        AssertionError: If status doesn't match
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.text[:500]}"
    )


def extract_json_value(
    json_data: Dict[str, Any],
    key_path: str,
    default: Any = None
) -> Any:
    """
    Extract value from nested JSON using dot notation.
    
    Args:
        json_data: JSON data as dictionary
        key_path: Dot-separated path to value (e.g., "user.profile.name")
        default: Default value if key not found
        
    Returns:
        Value at key_path or default
    """
    keys = key_path.split('.')
    value = json_data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value
