from fastapi import FastAPI, APIRouter
from app.core.config import API_NAME, VERSION, API_PREFIX, DEBUG
from app.api.main_router import router

def get_app() -> FastAPI:
    app = FastAPI(title=API_NAME, debug=DEBUG, version=VERSION)

    app.include_router(router, prefix=API_PREFIX)
    return app


app = get_app()