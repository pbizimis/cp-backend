from fastapi import APIRouter, Depends, Security, Query
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.mongodb import DeletionOptions
from app.schemas.stylegan_user import StyleGanUser
from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

router = APIRouter()

@router.get("/images")
async def user_images(db: AsyncIOMotorClient = Depends(get_db),  user: Auth0User = Security(auth.get_user, scopes=["use:all"]), stylegan_user_class = Depends(StyleGanUser.get_class)) -> dict:

    stylegan_user = stylegan_user_class(user, db)

    all_image_ids = await stylegan_user.get_images()

    return {"image_url_prefix": IMAGE_STORAGE_BASE_URL, "image_ids": all_image_ids}

@router.delete("/images")
async def user_images(deletion_options: DeletionOptions, db: AsyncIOMotorClient = Depends(get_db),  user: Auth0User = Security(auth.get_user, scopes=["use:all"]), stylegan_user_class = Depends(StyleGanUser.get_class)) -> dict:

    stylegan_user = stylegan_user_class(user, db)

    await stylegan_user.delete_images(deletion_options)

    deleted_images = "all" if deletion_options.all_documents else deletion_options.id_list

    return {"deleted_images": deleted_images}