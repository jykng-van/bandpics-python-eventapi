import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from contextlib import asynccontextmanager, contextmanager
from fastapi import FastAPI

load_dotenv() # load environment variables from .env file


# for the database connection
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Start the database connection
    print(app)
    print("MongoBD startup")
    mongo_connection = connect_to_db()
    print(mongo_connection)
    #app.db = next(mongo_connection)
    app.db = mongo_connection
    app.client = app.db.client


    yield
    # Close the database connection
    await shutdown_db_client(app)

# method to connect to the MongoDb Connection for dependency injection
def connect_to_db():
    print('DB Connection', os.getenv('MONGO_DB_CONNECTION_STRING'))
    client = AsyncMongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
    print(client)
    print('DB Name', os.getenv('MONGO_DB_NAME'))
    db = client[os.getenv('MONGO_DB_NAME')]
    return db




# method to close the database connection
async def shutdown_db_client(app):
    await app.client.close()
    print("Database disconnected.")