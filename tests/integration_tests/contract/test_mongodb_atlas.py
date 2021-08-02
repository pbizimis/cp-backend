import datetime
import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.mongodb import (close_db, delete_image, get_db, get_user_images,
                            save_image)
from app.schemas.mongodb import Image

current_date = datetime.datetime(2020, 2, 2, 20, 20, 20)


@pytest.mark.asyncio
async def test_db_correct_cases(mocker):
    conn_str = f"mongodb+srv://admin:{os.environ['MONGOPW']}@cluster0.bgniv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    client = AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    mocker.patch("app.db.mongodb.db_name", "testing")

    image_data = {
        "url": "url1",
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }
    image = Image(**image_data)

    # save one image
    await save_image(client, image)
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 1
    assert images == [
        Image(url="url1", auth0_id="007", creation_date=current_date, method={})
    ]

    image_data = {
        "url": "url2",
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }
    image = Image(**image_data)

    # save another image
    await save_image(client, image)
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 2
    assert images == [
        Image(url="url1", auth0_id="007", creation_date=current_date, method={}),
        Image(url="url2", auth0_id="007", creation_date=current_date, method={}),
    ]

    # save image for different user
    image_data = {
        "url": "url1",
        "auth0_id": "008",
        "creation_date": current_date,
        "method": {},
    }
    image = Image(**image_data)
    await save_image(client, image)
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 2
    assert images == [
        Image(url="url1", auth0_id="007", creation_date=current_date, method={}),
        Image(url="url2", auth0_id="007", creation_date=current_date, method={}),
    ]

    # delete image for user 007
    result = await delete_image(client, "007", "url1")
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 1
    assert images == [
        Image(url="url2", auth0_id="007", creation_date=current_date, method={})
    ]

    # delete image for user 007
    result = await delete_image(client, "007", "url2")
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 0
    assert images == []

    # delete image for user 008
    result = await delete_image(client, "008", "url1")
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(client, "008")
    assert len(images) == 0
    assert images == []


@pytest.mark.asyncio
async def test_db_wrong_cases(mocker):
    conn_str = f"mongodb+srv://admin:{os.environ['MONGOPW']}@cluster0.bgniv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    client = AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    mocker.patch("app.db.mongodb.db_name", "testing")

    # data needs to be a pydantic object
    with pytest.raises(AttributeError):
        await save_image(client, {"not a": "pydantic object"})

    # user not in db (has no images)
    images = await get_user_images(client, "007")
    assert len(images) == 0
    assert images == []

    # delete not existing image
    result = await delete_image(client, "007", "url")
    assert result.deleted_count == 0
