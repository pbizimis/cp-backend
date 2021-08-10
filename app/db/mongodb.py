import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import DeleteResult, InsertOneResult

from app.core.config import MONGO_COLLECTION_NAME, MONGO_DB_NAME
from app.schemas.mongodb import ImageData, MongoClient

mongodb = MongoClient()


async def get_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str
) -> list:
    """Get all images of a user from mongodb.

    Args:
        mongodb (AsyncIOMotorClient): the mongodb database connection
        auth0_id (str): the user auth0 id

    Returns:
        list: a list with all image ids
    """
    cursor = mongodb[MONGO_DB_NAME][MONGO_COLLECTION_NAME].find({"auth0_id": auth0_id})
    all_user_images = []
    async for image_data in cursor:
        image = ImageData(**image_data)
        all_user_images.append(image)

    return all_user_images


async def save_user_image_in_mongodb(
    mongodb: AsyncIOMotorClient, image_data: ImageData
) -> InsertOneResult:
    """Save an image and its data in mongodb.

    Args:
        mongodb (AsyncIOMotorClient): the mongodb database connection
        image_data (ImageData): a pydantic model object containing the image data

    Returns:
        InsertOneResult: a mongodb result
    """
    return await mongodb[MONGO_DB_NAME][MONGO_COLLECTION_NAME].insert_one(
        image_data.dict()
    )


async def delete_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str, image_id_list: list
) -> DeleteResult:
    """Delete a list of images of a user from mongodb.

    Args:
        mongodb (AsyncIOMotorClient): the mongodb database connection
        auth0_id (str): the user auth0 id
        image_id_list (list): a list of ids that should be deleted

    Returns:
        DeleteResult: a mongodb result
    """
    return await mongodb[MONGO_DB_NAME][MONGO_COLLECTION_NAME].delete_many(
        {"auth0_id": auth0_id, "url": {"$in": image_id_list}}
    )


async def delete_all_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str
) -> DeleteResult:
    """Delete all images of a user from mongodb.

    Args:
        mongodb (AsyncIOMotorClient): the mongodb database connection
        auth0_id (str): the user auth0 id

    Returns:
        DeleteResult: a mongodb result
    """
    return await mongodb[MONGO_DB_NAME][MONGO_COLLECTION_NAME].delete_many(
        {"auth0_id": auth0_id}
    )
