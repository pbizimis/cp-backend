from app.db.mongodb import save_image, get_user_images, delete_all_images, delete_images, get_db, close_db
from app.schemas.mongodb import Image
import pytest
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import pytz

current_date = datetime.datetime(2020, 2, 2, 20, 20, 20)


@pytest.mark.asyncio
async def test_get_db():
    client = await get_db()
    assert type(client) == AsyncIOMotorClient

    await close_db()
    assert True


@pytest.mark.asyncio
async def test_db_correct_cases(async_mongodb):

    image_data = {
        "url": "url1",
        "auth0_id": "007",
        "creation_date": current_date,
        "method": {},
    }
    image = Image(**image_data)

    # save one image
    await save_image(async_mongodb, image)
    # get images
    images = await get_user_images(async_mongodb, "007")
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
    await save_image(async_mongodb, image)
    # get images
    images = await get_user_images(async_mongodb, "007")
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
    await save_image(async_mongodb, image)
    # get images
    images = await get_user_images(async_mongodb, "007")
    assert len(images) == 2
    assert images == [
        Image(url="url1", auth0_id="007", creation_date=current_date, method={}),
        Image(url="url2", auth0_id="007", creation_date=current_date, method={}),
    ]

    # delete image for user 007
    result = await delete_images(async_mongodb, "007", ["url1"])
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(async_mongodb, "007")
    assert len(images) == 1
    assert images == [
        Image(url="url2", auth0_id="007", creation_date=current_date, method={})
    ]

    # delete image for user 008
    result = await delete_images(async_mongodb, "008", ["url1"])
    assert result.deleted_count == 1
    # get images
    images = await get_user_images(async_mongodb, "008")
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
        await save_image(async_mongodb, image)

    images = await get_user_images(async_mongodb, "007")
    assert len(images) == 11

    # delete all images for user 007
    result = await delete_all_images(async_mongodb, "007")
    assert result.deleted_count == 11



@pytest.mark.asyncio
async def test_db_wrong_cases(async_mongodb):

    # data needs to be a pydantic object
    with pytest.raises(AttributeError):
        await save_image(async_mongodb, {"not a": "pydantic object"})

    # user not in db (has no images)
    images = await get_user_images(async_mongodb, "007")
    assert len(images) == 0
    assert images == []

    # delete not existing image
    result = await delete_images(async_mongodb, "007", ["url"])
    assert result.deleted_count == 0
