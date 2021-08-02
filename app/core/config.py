import os

API_NAME = "CP_API"
VERSION = "0.0.1"
API_PREFIX = "/api/v1"
DEBUG = True
IMAGE_STORAGE_BASE_URL = "https://images.webdesigan.com/"
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API = os.getenv("AUTH0_API")