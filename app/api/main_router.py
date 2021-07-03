from fastapi import APIRouter
from app.api.routes import generation
from app.api.routes import style_mixing

router = APIRouter()
router.include_router(generation.router, tags=["Generation"])
router.include_router(style_mixing.router, tags=["Style Mixing"])