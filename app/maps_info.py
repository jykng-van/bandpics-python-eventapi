import os
from dotenv import load_dotenv
import requests
from enum import Enum
import json
import math



class SearchType(Enum): # Enum for search types
    DEFAULT = 1 # Default search type
    EXPANDED = 2 # Expanded search type
    UNRESTRICTED = 3 # Unrestricted search type


class MapsInfo:
    R = 6371000  # radius of Earth in meters

    def __init__(self):
        load_dotenv() # load environment variable from .env

    def get_location(self, coords, search_type:SearchType=SearchType.DEFAULT, search_radius:float=50.0):

        # set search radius and included types based on search type
        if search_type == SearchType.DEFAULT:
            included_types = ['event_venue','night_club']
            rank_preference = 'DISTANCE'
        elif search_type == search_type.EXPANDED:
            included_types = ['event_venue','night_club','bar','concert_hall','performing_arts_theater','amphitheatre','opera_house','stadium','arena',
                              'community_center','sports_activity_location']
            rank_preference = 'POPULARITY'
        else:
            included_types = []
            rank_preference = 'DISTANCE'


        url = 'https://places.googleapis.com/v1/places:searchNearby' # Google Places Search Nearby API url
        location_restriction = { # location restriction
            'circle': {
                'center': coords, # coordinates of the center
                'radius': search_radius
            }
        }
        payload = { # json payload for the request
            'includedTypes':included_types,
            'locationRestriction': location_restriction,
            'rankPreference': rank_preference,
        }
        field_masks = 'places.name,places.displayName,places.formatted_address,places.address_components,places.types,places.location' # fields to include in the response
        headers = { # request headers for the api
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': os.getenv('GOOGLE_MAPS_API_KEY'), # API key from .env file that's essential for the places API request
            'X-Goog-FieldMask': field_masks
        }
        r = requests.post(url, json=payload, headers=headers) # send the API request
        if r.status_code == 200:
            json = r.json()
            places = json.get('places', [])
            #add calculated distance of each place location from coords
            places = [dict(p, **{'distance': self.haversine(coords, p['location']) if 'location' in p else None}) for p in places]
            return {
                'places': places, # places results
                'locationRestriction': location_restriction, # location restriction used in request
                'search_type': search_type.name, # search type of request
                'included_types': included_types, # included types to search for
                'rank_preference': rank_preference, # rank preference used
            }
        else:
            return r.content

    # get the distance between two coordinates using Haversine formula
    def haversine(self, coords1, coords2):
        lat1, lng1, lat2, lng2 = [coords1['latitude'], coords1['longitude'], coords2['latitude'], coords2['longitude']] # get lat and lng from coords1 and coords2

        d_lat = math.radians(lat2 - lat1) # get difference in latitudes in radians
        d_lng = math.radians(lng2 - lng1) # get difference in longitudes in radians
        rad_lat1 = math.radians(lat1) # lat1 in radians
        rad_lat2 = math.radians(lat2) # lat2 in radians

        # calculate the distance using Haversine formula in meters
        a = math.sin(d_lat / 2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lng / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = self.R * c

        #distance = self.R * 2 * math.asin(math.sqrt(math.sin(d_lat / 2) ** 2 + math.sin(d_lng / 2) ** 2 * math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))))
        return distance