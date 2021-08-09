import os
from datetime import timedelta

API_NAME = "CP_API"
VERSION = "0.0.1"
API_PREFIX = "/api/v1"
DEBUG = True
IMAGE_STORAGE_BASE_URL = "https://images.webdesigan.com/"
# Auth0
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API = os.getenv("AUTH0_API")
# Redis
REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_RATELIMIT_REQUESTS = int(os.getenv("REDIS_RATELIMIT_REQUESTS"))
REDIS_RATELIMIT_PERIOD = timedelta(
    minutes=int(os.getenv("REDIS_RATELIMIT_PERIOD_MINUTES"))
)
