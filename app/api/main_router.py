from fastapi import APIRouter
from app.api.routes import stylegan2ada

router = APIRouter()
router.include_router(stylegan2ada.router, prefix="/stylegan2ada", tags=["StyleGan2 ADA"])