import aioredis
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.main_router import router
from app.core.config import API_NAME, API_PREFIX, DEBUG, MONGO_URL, REDIS_URL, VERSION
from app.db.mongodb import mongodb
from app.db.redisdb import redisdb


def get_app() -> FastAPI:
    """Create a new FastAPI app."""
    app = FastAPI(title=API_NAME, debug=DEBUG, version=VERSION)

    app.include_router(router, prefix=API_PREFIX)

    # CORS config
    origins = ["http://localhost:3000", "https://webdesigan.com"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
        allow_headers=["*"],
    )

    return app


app = get_app()


@app.on_event("startup")
async def startup_event():
    """Handle the startup event of the main application."""
    mongodb.client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    redisdb.client = await aioredis.from_url(REDIS_URL)


@app.on_event("shutdown")
async def shutdown_event():
    """Handle the shutdown event of the main application."""
    await mongodb.client.close()
    await redisdb.client.close()
