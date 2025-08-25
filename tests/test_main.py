from unittest.mock import MagicMock, AsyncMock
from io import BytesIO, BufferedReader
from PIL import Image
import pytest
from mongomock import MongoClient
from datetime import datetime, timezone
from http import HTTPStatus

from bson.objectid import ObjectId

from app.main import app
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
    print(json)
    assert response.status_code == HTTPStatus.OK
    assert json['name'] == 'test', "Event name does not match"


