from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main_router import router
from app.core.config import API_NAME, API_PREFIX, DEBUG, VERSION


def get_app() -> FastAPI:
    app = FastAPI(title=API_NAME, debug=DEBUG, version=VERSION)

    app.include_router(router, prefix=API_PREFIX)

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
