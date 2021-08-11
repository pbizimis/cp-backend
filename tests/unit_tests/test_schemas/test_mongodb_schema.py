import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas.mongodb import DeletionOptions, MongoClient


def test_mongodb_get_client():
    """Unit test MongoDB client retrieval."""
    test_mongodb = MongoClient()
    test_mongodb.client = AsyncIOMotorClient()

    test_mongodb_client = test_mongodb.get_client()
    assert type(test_mongodb_client) == AsyncIOMotorClient


def test_deletion_options_validation():
    """Unit test the validation of the id_list attribute."""
    DeletionOptions(id_list=["ea55a984b67346afab069fb6a34adcc3", "ea55a984b67346afab069fb6a34adcc3"])
    with pytest.raises(ValueError):
        DeletionOptions(id_list=[1234213, "ea55a984b67346afab069fb6a34adcc3"])
    with pytest.raises(ValueError):
        DeletionOptions(id_list=[1234213, "ea55a984b67346afab069fb6a34adcc3"])
    with pytest.raises(ValueError):
        DeletionOptions(id_list=["Wrong", "Wrong"])
