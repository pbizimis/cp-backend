import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import DeleteResult, InsertOneResult

from app.schemas.mongodb import ImageData

# database only connects with first query
conn_str = f"mongodb+srv://admin:{os.environ['MONGOPW']}@cluster0.bgniv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
db_name = "development"
db_collection_images = "images"


async def close_mongodb() -> None:
    client.close()


async def get_mongodb() -> AsyncIOMotorClient:
    return client


async def get_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str
) -> list:
    cursor = mongodb[db_name][db_collection_images].find({"auth0_id": auth0_id})
    all_user_images = []
    async for image_data in cursor:
        image = ImageData(**image_data)
        all_user_images.append(image)

    return all_user_images


async def save_user_image_in_mongodb(
    mongodb: AsyncIOMotorClient, image_data: ImageData
) -> InsertOneResult:
    return await mongodb[db_name][db_collection_images].insert_one(image_data.dict())


async def delete_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str, image_id_list: list
) -> DeleteResult:
    return await mongodb[db_name][db_collection_images].delete_many(
        {"auth0_id": auth0_id, "url": {"$in": image_id_list}}
    )


async def delete_all_user_images_from_mongodb(
    mongodb: AsyncIOMotorClient, auth0_id: str
) -> DeleteResult:
    return await mongodb[db_name][db_collection_images].delete_many(
        {"auth0_id": auth0_id}
    )
