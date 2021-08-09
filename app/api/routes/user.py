from typing import List

from fastapi import APIRouter, Depends, Query, Security
from fastapi_auth0 import Auth0User
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.auth0 import auth
from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.mongodb import get_mongodb
from app.schemas.mongodb import DeletionOptions
from app.schemas.stylegan_user import StyleGanUser

router = APIRouter()


@router.get("/images")
async def get_user_images(
    mongodb: AsyncIOMotorClient = Depends(get_mongodb),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
    stylegan_user_class=Depends(StyleGanUser.get_class),
) -> dict:

    stylegan_user = stylegan_user_class(user, mongodb)

    all_image_ids = await stylegan_user.get_user_images()

    return {"image_url_prefix": IMAGE_STORAGE_BASE_URL, "image_ids": all_image_ids}


@router.delete("/images")
async def delete_user_images(
    deletion_options: DeletionOptions,
    mongodb: AsyncIOMotorClient = Depends(get_mongodb),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
    stylegan_user_class=Depends(StyleGanUser.get_class),
) -> dict:

    stylegan_user = stylegan_user_class(user, mongodb)

    await stylegan_user.delete_user_images(deletion_options)

    deleted_images = (
        "all" if deletion_options.all_documents else deletion_options.id_list
    )

    return {"deleted_images": deleted_images}
