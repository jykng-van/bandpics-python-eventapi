from unittest.mock import MagicMock, AsyncMock
from io import BytesIO, BufferedReader
from PIL import Image
import pytest
from mongomock import MongoClient
from datetime import datetime, timezone
from http import HTTPStatus

from bson.objectid import ObjectId

from app.main import app, setup_maps_info
from app.db import connect_to_db

# test list_events
@pytest.mark.asyncio
async def test_list_images(client, mock_mongodb_live_events_initialized):
    # we're using our mock_mongodb_live_events_initialized fixture which has image_groups and images initialized
    app.dependency_overrides[connect_to_db] = mock_mongodb_live_events_initialized
    response = client.get("/events")

    json = response.json()
    print(json)
    assert response.status_code == HTTPStatus.OK
    assert len(json) > 0, "No events found" # check if any events are present
    assert json[0]['name'] == 'test', "Event name does not match"

# test get_event
@pytest.mark.asyncio
async def test_get_event(client, mock_mongodb_live_events_initialized, get_event_id):
    # we're using our mock_mongodb_live_events_initialized fixture which has image_groups and images initialized
    app.dependency_overrides[connect_to_db] = mock_mongodb_live_events_initialized
    response = client.get("/events/" + str(get_event_id))

    json = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json['name'] == 'test', "Event name does not match"

# test get_event not found
@pytest.mark.asyncio
async def test_get_event_404(client, mock_mongodb_live_events_initialized):
    # we're using our mock_mongodb_live_events_initialized fixture which has image_groups and images initialized
    app.dependency_overrides[connect_to_db] = mock_mongodb_live_events_initialized
    response = client.get("/events/"+ str(ObjectId('bbbbbbbbbbbbbbbbbbbbbbbb')))

    json = response.json()
    assert response.status_code == HTTPStatus.NOT_FOUND

# test create_event
@pytest.mark.asyncio
async def test_create_event(client, mock_mongodb):
    app.dependency_overrides[connect_to_db] = mock_mongodb
    event_name = 'new event'
    event_date = '2025-01-01'
    event = {
        'event':{
            'name': event_name,
            'description': 'new event description',
            'event_date': event_date
        }
    }
    response = client.post("/events", json=event)
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert json['name'] == event_name, "Event name does not match"
    assert json['event_date'] == event_date, "Event date does not match"

# test update_event
@pytest.mark.asyncio
async def test_update_event(client, mock_mongodb_live_events_initialized, get_event_id):
    app.dependency_overrides[connect_to_db] = mock_mongodb_live_events_initialized
    event_name = 'updated event'
    event_date = '2025-12-31'
    event = {
        'event':{
            'name':event_name,
            'description': 'updated event description',
            'event_date': event_date
        }
    }
    response = client.patch("/events/" + str(get_event_id), json=event)
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert json['name'] == event_name, "Event name does not match"
    assert json['event_date'] == event_date, "Event date does not match"

# test delete_event
@pytest.mark.asyncio
async def test_delete_event(client, mock_mongodb_live_events_initialized, get_event_id):
    app.dependency_overrides[connect_to_db] = mock_mongodb_live_events_initialized
    response = client.delete("/events/" + str(get_event_id))
    assert response.status_code == HTTPStatus.OK

    #try to find deleted event
    #check if the group and the images are deleted
    db = app.db
    event_collection = db.get_collection('live_events')
    event = await event_collection.find_one({'_id': get_event_id})
    assert event is None, "Event not deleted"

# test get_places
@pytest.mark.asyncio
async def test_get_places(client, mock_maps_info):
    app.dependency_overrides[setup_maps_info] = mock_maps_info

    response = client.get(f"/locations/?lat=12.3&lng=45.6")
    assert response.status_code == HTTPStatus.OK


