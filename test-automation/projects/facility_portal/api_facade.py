"""
API Facade for Facility Portal.

High-level API interface that encapsulates all API interactions
for the Facility Portal project.
"""
from typing import List, Dict, Any

import requests

from infra.base.base_api import BaseApi
from infra.utils.logger import get_logger

logger = get_logger(__name__)


class FacilityPortalApiFacade:
    """
    High-level API facade for Facility Portal.
    
    Provides simplified methods for test cases, encapsulating all API
    interactions for facility management.
    
    Usage in tests:
        def test_facilities(self):
            facilities = self.api.facility_portal.get_facilities()
            assert isinstance(facilities, list)
    """
    
    def __init__(self, session: requests.Session, base_url: str):
        """
        Initialize FacilityPortalApiFacade.
        
        Args:
            session: Requests Session instance
            base_url: Base URL for the API (e.g., "https://api.example.com")
        """
        self.session = session
        self.base_url = base_url.rstrip('/')
        self.api_client = BaseApi(base_url)
        # Share the session with the base API client
        self.api_client.session = session
        logger.info(f"Initialized FacilityPortalApiFacade with base_url: {base_url}")
    
    def get_facilities(self) -> List[Dict[str, Any]]:
        """
        Get list of all facilities.
        
        TODO: Update endpoint to match actual API
        TODO: Add proper error handling and response validation
        
        Returns:
            List of facility dictionaries
        """
        logger.info("Getting facilities list")
        
        try:
            # TODO: Replace '/facilities' with actual endpoint
            response = self.api_client.get('/facilities')
            
            if response.status_code == 200:
                facilities = response.json()
                logger.info(f"Retrieved {len(facilities)} facilities")
                return facilities
            else:
                logger.warning(f"Failed to get facilities, status: {response.status_code}")
                # Return empty list on failure for now
                return []
        except Exception as e:
            logger.error(f"Error getting facilities: {e}")
            # Return empty list on error for placeholder implementation
            return []
