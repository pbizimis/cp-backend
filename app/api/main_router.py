from fastapi import APIRouter
from app.api.model_routes import generate

router = APIRouter()
router.include_router(generate.router, tags=["Generation"], prefix="/generate")