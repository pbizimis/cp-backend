import datetime
import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import MONGO_URL
from app.db.mongodb import (
    delete_all_user_images_from_mongodb,
    delete_user_images_from_mongodb,
    get_user_images_from_mongodb,
    save_user_image_in_mongodb,
)
from app.schemas.mongodb import ImageData

current_date = datetime.datetime(2020, 2, 2, 20, 20, 20)


@pytest.mark.asyncio
async def test_mongodb_correct_cases(mocker):
    """Test application logic against an instance of MongoDB Atlas. This test tests correct cases."""

    mongodb_client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    mocker.patch("app.db.mongodb.MONGO_DB_NAME", "testing")

    ###
    # Test saving

    # Save first mock image
    image_data = {
        "url": "url1",
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }
    image = ImageData(**image_data)

    await save_user_image_in_mongodb(mongodb_client, image)

    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 1
    assert images == [
        ImageData(url="url1", auth0_id="007", creation_date=current_date, method={})
    ]

    # Save second mock image
    image_data = {
        "url": "url2",
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }
    image = ImageData(**image_data)

    await save_user_image_in_mongodb(mongodb_client, image)
    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 2
    assert images == [
        ImageData(url="url1", auth0_id="007", creation_date=current_date, method={}),
        ImageData(url="url2", auth0_id="007", creation_date=current_date, method={}),
    ]

    # Save image for different user
    image_data = {
        "url": "url1",
        "auth0_id": "008",
        "creation_date": current_date,
        "method": {},
    }
    image = ImageData(**image_data)
    await save_user_image_in_mongodb(mongodb_client, image)

    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 2
    assert images == [
        ImageData(url="url1", auth0_id="007", creation_date=current_date, method={}),
        ImageData(url="url2", auth0_id="007", creation_date=current_date, method={}),
    ]

    ###
    # Test deletion

    # Delete image for user 007
    result = await delete_user_images_from_mongodb(
        mongodb_client, "007", ["url1", "url2"]
    )
    assert result.deleted_count == 2

    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 0
    assert images == []

    # Delete image for user 008
    result = await delete_user_images_from_mongodb(mongodb_client, "008", ["url1"])
    assert result.deleted_count == 1

    images = await get_user_images_from_mongodb(mongodb_client, "008")
    assert len(images) == 0
    assert images == []

    ###
    # Test deletion of all

    # Save multiple images for user 007
    image_data = {
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }

    list_of_images = [ImageData(url=i, **image_data) for i in range(10)]

    for image in list_of_images:
        await save_user_image_in_mongodb(mongodb_client, image)

    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 10

    # Delete all images for user 007
    result = await delete_all_user_images_from_mongodb(mongodb_client, "007")
    assert result.deleted_count == 10


@pytest.mark.asyncio
async def test_mongodb_wrong_cases(mocker):
    """Test application logic against an instance of MongoDB Atlas. This test tests wrong cases."""

    mongodb_client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    mocker.patch("app.db.mongodb.MONGO_DB_NAME", "testing")

    # Data needs to be a pydantic object
    with pytest.raises(AttributeError):
        await save_user_image_in_mongodb(mongodb_client, {"not a": "pydantic object"})

    # User is not in db (has no images)
    images = await get_user_images_from_mongodb(mongodb_client, "007")
    assert len(images) == 0
    assert images == []

    # Delete not existing image
    result = await delete_user_images_from_mongodb(mongodb_client, "007", ["url"])
    assert result.deleted_count == 0
