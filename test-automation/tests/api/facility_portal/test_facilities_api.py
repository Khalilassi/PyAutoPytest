"""
Test cases for Facility Portal API.

Example API tests using project facades.
Tests demonstrate high-level API usage without direct requests calls.
"""
import pytest


@pytest.mark.api
class TestFacilityApi:
    """
    Test cases for Facility Portal API using FacilityPortalApiFacade.
    
    Tests use self.api.facility_portal facade for all API interactions.
    No direct requests.get/post calls in tests - all logic is in facades.
    """
    
    @pytest.mark.skip(reason="Placeholder - requires real API endpoint")
    def test_get_facilities(self, requests_session):
        """
        Test getting list of facilities using high-level facade API.
        
        This test demonstrates the new pattern:
        - No requests.get() or session.post() in test code
        - All API interactions are through self.api.facility_portal facade
        - Test only contains high-level actions and assertions
        
        TODO: Enable when API is available
        """
        # Get facilities using facade - encapsulates all API logic
        facilities = self.api.facility_portal.get_facilities()
        
        # Verify response is a list
        assert isinstance(facilities, list), "get_facilities should return a list"
    
    @pytest.mark.skip(reason="Placeholder - requires real API endpoint")  
    def test_get_facilities_not_empty(self, requests_session):
        """
        Test that facilities list is not empty.
        
        TODO: Enable when API is available and has data
        """
        facilities = self.api.facility_portal.get_facilities()
        
        assert len(facilities) > 0, "Should have at least one facility"
