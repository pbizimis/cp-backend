from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas.mongodb import MongoClient


def test_mongodb_get_client():
    """Unit test MongoDB client retrieval."""
    test_mongodb = MongoClient()
    test_mongodb.client = AsyncIOMotorClient()

    test_mongodb_client = test_mongodb.get_client()
    assert type(test_mongodb_client) == AsyncIOMotorClient
