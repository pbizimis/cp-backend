import datetime

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.mongodb import (close_db, delete_images, delete_all_images, get_db, get_user_images,
                            save_image)
from app.schemas.mongodb import Image

current_date = datetime.datetime(2020, 2, 2, 20, 20, 20)


@pytest.mark.asyncio
async def test_db_correct_cases():
    client = AsyncIOMotorClient("localhost", 27017)

    # make sure that db is empty
    result = await delete_all_images(client, "007")
    result = await delete_all_images(client, "008")

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
    result = await delete_images(client, "007", ["url1", "url2"])
    assert result.deleted_count == 2
    # get images
    images = await get_user_images(client, "007")
    assert len(images) == 0
    assert images == []

    # delete image for user 008
    result = await delete_images(client, "008", ["url1"])
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(client, "008")
    assert len(images) == 0
    assert images == []

    # save many images
    image_data = {
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }

    list_of_images = [Image(url=i, **image_data) for i in range(10)]

    # save multiple image
    for image in list_of_images:
        await save_image(client, image)

    images = await get_user_images(client, "007")
    assert len(images) == 10

    # delete all images for user 007
    result = await delete_all_images(client, "007")
    assert result.deleted_count == 10

@pytest.mark.asyncio
async def test_db_wrong_cases():
    client = AsyncIOMotorClient("localhost", 27017)

    # data needs to be a pydantic object
    with pytest.raises(AttributeError):
        await save_image(client, {"not a": "pydantic object"})

    # user not in db (has no images)
    images = await get_user_images(client, "007")
    assert len(images) == 0
    assert images == []

    # delete not existing image
    result = await delete_images(client, "007", ["url"])
    assert result.deleted_count == 0
