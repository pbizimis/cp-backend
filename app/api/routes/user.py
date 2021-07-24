from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.stylegan_user import StyleGanUser
from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

@router.get("/images")
async def style_mix_images(db: AsyncIOMotorClient = Depends(get_db),  user: Auth0User = Security(auth.get_user, scopes=["use:all"])):

    stylegan_user = StyleGanUser(user, db)

    all_image_ids = await stylegan_user.get_images()

    return {"image_url_prefix": IMAGE_STORAGE_BASE_URL, "image_ids": all_image_ids}