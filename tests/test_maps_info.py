import unittest
from unittest.mock import patch, MagicMock

from app.maps_info import MapsInfo, SearchType
import math

class TestMapsInfo(unittest.TestCase):
    def test_haversine_same_coords(self):
        coords1 = {'latitude':12.34, 'longitude':56.78}
        coords2 = {'latitude':12.34, 'longitude':56.78}

        maps_info = MapsInfo()
        distance = maps_info.haversine(coords1, coords2)

        assert distance == 0.0, "Distance should be 0.0 if coordinates are the same"

    def test_haversine_opposite_coords(self):
        coords1 = {'latitude':12.34, 'longitude':-56.78}
        lat2 = -(coords1['latitude']) # just invert the latitude, because latitude is based on the equator and goes from 0 to +/-90 degrees
        lng2 = coords1['longitude'] + (180 if coords1['longitude'] < 0 else -180) # opposite longitude, because prime meridian is in Greenwich, UK and goes from 0 to +/-180 degrees
        coords2 = {'latitude':lat2, 'longitude':lng2} #antipodal coordinates

        maps_info = MapsInfo()
        distance = maps_info.haversine(coords1, coords2)
        half_circumference = maps_info.R * math.pi
        print(distance, half_circumference)

        assert distance == half_circumference, "Distance should be half the circumference of the Earth if coords are opposite"


    def mocked_post_request(*args, **kwargs):
        # Mocking requests.post to simulate the behaviour in get_location
        class mock_post():
            def __init__(self, json_data, status_code, content=None):
                self.json_data = json_data # Mock json data
                self.status_code = status_code # Mock status code
                self.content = content # Mock content

            def json(self):
                return self.json_data

        if 'places.googleapis.com' in args[0]:
            # places.name,places.displayName,places.formatted_address,places.types,places.location
            return mock_post(status_code=200, json_data={
                'places':[{
                    'name':'apsdoifjas34asdfasdf',
                    'displayName':'Test Place',
                    'formatted_address':'123 Test St, Testville, BC V0V 1A1',
                    'types':['event_venue','bar','night_club'],
                    'location':{
                        'latitude': 12.3401,
                        'longitude': 56.7801
                    }
                }]
            })
        else:
            return mock_post(status=400, json_data={}, content='Bad Request')

    @patch('requests.post', side_effect=mocked_post_request)
    def test_get_location(self, mock_post):
        coords = {'latitude':12.34, 'longitude':56.78}

        # Mock the API key
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'abc123'

        maps_info = MapsInfo()
        search_radius = 50.0
        location_results = maps_info.get_location(coords=coords, search_type=SearchType.DEFAULT, search_radius=search_radius)

        # location_restriction that should be used in the request
        location_restriction = {
            'circle':{
                'center':coords,
                'radius':search_radius
            }
        }
        print(location_results)
        assert location_results['locationRestriction'] == location_restriction, "location restriction doesn't match"
        assert 'places' in location_results, "places not found in results"
        assert len(location_results['places']) > 0, "places should return at least one result"

