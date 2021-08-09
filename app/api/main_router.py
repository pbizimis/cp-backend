from fastapi import APIRouter

from app.api.routes import stylegan2ada, stylegan_models, user

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(stylegan_models.router, tags=["StyleGan"])
router.include_router(
    stylegan2ada.router, prefix="/stylegan2ada", tags=["StyleGan2 ADA"]
)
