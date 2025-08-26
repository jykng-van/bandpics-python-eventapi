from typing import Union
from fastapi import FastAPI, Depends, HTTPException, Body
from typing_extensions import Annotated

from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from http import HTTPStatus

from app.db import lifespan, connect_to_db
from app.models import LiveEvent, UpdateLiveEvent

#from maps_info import MapsInfo
from PIL import Image
from bson.objectid import ObjectId
from pymongo import MongoClient, ReturnDocument
import json
import io
from datetime import datetime, timezone

from mangum import Mangum # Use mangum for AWS
from starlette.requests import Request
import asyncio

app = FastAPI(lifespan=lifespan) # start FastAPI with lifespan
print('app:',app)


# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Get all events
@app.get("/events", response_model=list[LiveEvent], response_model_by_alias=False, response_model_exclude_none=True,
         response_description="Get a list of all live events")
async def list_events(db=Depends(connect_to_db)) -> list[LiveEvent]:
    event_collection = db.get_collection("live_events")
    events = []
    async for event in event_collection.find():
        print(event)
        events.append(LiveEvent(**event))
    #events = event_collection.findAll()
    return events

# Get event by id
@app.get("/events/{event_id}", response_model=LiveEvent, response_model_by_alias=False, response_model_exclude_none=True,
         response_description="Gets a live events by id")
async def get_event(event_id: str, db=Depends(connect_to_db)) -> LiveEvent:
    event_collection = db.get_collection("live_events")
    #might need to use aggregate
    print(event_id)
    event = await event_collection.find_one({'_id': ObjectId(event_id)})
    if event:
        return event
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event with that ID not found")

# Create a new event
@app.post("/events", response_model=LiveEvent, response_model_by_alias=False, response_model_exclude_none=True,
          response_description="Create a new live event")
async def create_event(event:Annotated[UpdateLiveEvent, Body(embed=True)], db=Depends(connect_to_db)):
    #exclude None values from the live event
    print(event)
    print('Removing none from event')
    event = {
        k: v for k, v in event.model_dump(by_alias=True).items() if v is not None
    }
    if 'eventDate' in event: # convert string to date
        event['eventDate'] = datetime.strptime(event['eventDate'], '%Y-%m-%d')
    print(event)

    event_collection = db.get_collection("live_events")
    # prepare for insertion

    id = (await event_collection.insert_one(event)).inserted_id
    result_event = await event_collection.find_one({'_id': id})
    return result_event

# Update an event
@app.patch("/events/{event_id}", response_model=LiveEvent, response_model_by_alias=False, response_model_exclude_none=True,
          response_description="Update a live event")
async def update_event(event_id: str, event:Annotated[UpdateLiveEvent, Body(embed=True)], db=Depends(connect_to_db)):
    event_collection = db.get_collection("live_events")

    #exclude None values from the live event
    print(event)
    print('Removing none from event')
    event = {
        k: v for k, v in event.model_dump(by_alias=True).items() if v is not None
    }
    if len(event) > 0:
        if 'eventDate' in event: # convert string to date
            event['eventDate'] = datetime.strptime(event['eventDate'], '%Y-%m-%d')

        update_result = await event_collection.find_one_and_update(
            {'_id': ObjectId(event_id)},
            {'$set': event},
            return_document=ReturnDocument.AFTER
        )
        print('Update result:', update_result)
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event with that ID not found")
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event with that ID not found")

# Delete an event
@app.delete("/events/{event_id}", response_description="Delete a live event")
async def delete_event(event_id: str, db=Depends(connect_to_db)):
    event_collection = db.get_collection("live_events")
    delete_result = await event_collection.delete_one({'_id': ObjectId(event_id)})
    if delete_result.deleted_count > 0:
        return {"message": "Event deleted successfully"}
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event with that ID not found")


handler = Mangum(app=app, lifespan="off") # Use Mangum to handle AWS Lambda events

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8080)

#docker build -t bandpics-event-api .
#docker run -d --name event_api_dev -p 8000:8000 bandpics-event-api