from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas.mongodb import Image, User
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

async def create_user(db_con: AsyncIOMotorClient, image_data: dict) -> None:
    raise NotImplementedError

async def get_user(db_con: AsyncIOMotorClient, image_data: dict) -> None:
    raise NotImplementedError

async def get_user_images(db_con: AsyncIOMotorClient, image_data: dict) -> None:
    raise NotImplementedError

async def save_image(db_con: AsyncIOMotorClient, image_data: Image) -> None:
    await db_con[db_name][db_collection_user].insert_one(image_data.dict())
    await db_con[db_name][db_collection_images].insert_one(image_data.dict())