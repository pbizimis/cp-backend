from fastapi import APIRouter
from app.api.model_routes import get
from app.api.model_routes import post

router = APIRouter()
router.include_router(get.router, tags=["Generation"], prefix="/get")
router.include_router(post.router, tags=["Generation"], prefix="/post")