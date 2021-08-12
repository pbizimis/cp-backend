import os
from datetime import timedelta

API_NAME = "CP_API"
VERSION = "0.0.1"
API_PREFIX = "/api/v1"
DEBUG = bool(os.getenv("FASTAPI_DEBUG"))
IMAGE_STORAGE_BASE_URL = "https://images.webdesigan.com/"
# Auth0
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API = os.getenv("AUTH0_API")
# Redis
REDIS_URL = str(os.getenv("REDIS_URL"))
REDIS_RATELIMIT_REQUESTS = int(os.getenv("REDIS_RATELIMIT_REQUESTS"))
REDIS_RATELIMIT_PERIOD = timedelta(
    minutes=int(os.getenv("REDIS_RATELIMIT_PERIOD_MINUTES"))
)
# MongoDB
MONGO_URL = str(os.getenv("MONGO_URL"))
MONGO_DB_NAME = str(os.getenv("MONGO_DB_NAME"))
MONGO_COLLECTION_NAME = str(os.getenv("MONGO_COLLECTION_NAME"))
