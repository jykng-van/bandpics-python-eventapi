from pytest import fixture
from unittest.mock import MagicMock, AsyncMock
#from mongomock import MongoClient
from mongomock_motor import AsyncMongoMockClient
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime

class MockMongoClient:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self.db

    def __exit__(self, *args):
        pass

    def get_collection(self, name): # Mocking get_collection because the MockMongoClient doesn't have it
        return self.db.get_collection(name)

#empty db for testing
@fixture
def mock_mongodb():
    def mock_get_mongodb():
        from app.main import app
        mock_client = AsyncMongoMockClient()

        app.db = mock_client.db #to set the app's db to the mock db

        return MockMongoClient(mock_client.db)

    return mock_get_mongodb

test_event_id = ObjectId('aaaaaaaaaaaaaaaaaaaaaaa1')
test_date = datetime(2025,1,1,0,0,0)
test_created_at = datetime(2025,1,1,0,0,0)

test_event = {
    'name':'test',
    'description':'test description',
    'eventDate': test_date,
    '_id': test_event_id,
    'created_id':test_created_at,
    'updated_at':test_created_at,
}

# DB with event groups for testing
@fixture
def mock_mongodb_live_events_initialized():
    async def mock_get_mongodb():
        from app.main import app

        print('mock mongo image groups initialized')
        mock_client = AsyncMongoMockClient()

        await mock_client.db.live_events.insert_one(test_event)


        app.db = mock_client.db #to set the app's db to the mock db

        return MockMongoClient(mock_client.db)

    return mock_get_mongodb




@fixture
def client():
    # we patch auth within our client fixture
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@fixture
def get_event_id():
    return test_event_id

def mock_executor():
    def mock_get_executor():
        return MagicMock()

    return mock_get_executor

