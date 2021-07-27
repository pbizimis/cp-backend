from fastapi import FastAPI, APIRouter
from app.core.config import API_NAME, VERSION, API_PREFIX, DEBUG
from app.api.main_router import router
from fastapi.middleware.cors import CORSMiddleware

def get_app() -> FastAPI:
    app = FastAPI(title=API_NAME, debug=DEBUG, version=VERSION)

    origins = ["http://localhost:3000", "https://webdesigan.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix=API_PREFIX)
    return app


app = get_app()