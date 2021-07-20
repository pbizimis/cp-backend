from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas.mongodb import Image
import os

# database only connects with first query
conn_str = f"mongodb+srv://admin:{os.environ['MONGOPW']}@cluster0.bgniv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
db_name = "development"
db_collection_user = "users"
db_collection_images = "images"


async def close_db() -> None:
    client.close()

async def get_db() -> AsyncIOMotorClient:
    return client

async def get_user_images(db_con: AsyncIOMotorClient, auth0_id: str) -> list:
    cursor = db_con[db_name][db_collection_images].find({"auth0_id": auth0_id})
    all_user_images = []
    async for image_data in cursor:
        image = Image(**image_data)
        all_user_images.append(image)

    return all_user_images

async def save_image(db_con: AsyncIOMotorClient, auth0_id: str, image_data: Image) -> None:
    await db_con[db_name][db_collection_images].insert_one(image_data.dict())

async def delete_image(db_con: AsyncIOMotorClient, auth0_id: str, url: str) -> None:
    await db_con[db_name][db_collection_images].delete_one({"auth0_id": auth0_id, "url": url})