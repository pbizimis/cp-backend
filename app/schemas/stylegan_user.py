from __future__ import annotations

from typing import Type, Union

from fastapi_auth0 import Auth0User
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.google_cloud_storage import (
    delete_blob_from_gcs,
    download_blob_from_gcs,
    upload_blob_to_gcs,
)
from app.db.mongodb import (
    delete_all_user_images_from_mongodb,
    delete_user_images_from_mongodb,
    get_user_images_from_mongodb,
    save_user_image_in_mongodb,
)
from app.schemas.mongodb import DeletionOptions, ImageData
from app.schemas.stylegan_models import StyleGanModel


class StyleGanUser:
    def __init__(
        self,
        user: Auth0User,
        mongodb: AsyncIOMotorClient,
        stylegan_class: Type[StyleGanModel] = None,
        stylegan_method_options: dict = None,
    ) -> None:
        self.user = user
        self.stylegan_method_options = stylegan_method_options
        self.stylegan_class = stylegan_class
        self.mongodb = mongodb
        if self.stylegan_class:
            self.stylegan_model = self._load_stylegan_model()

    def _load_stylegan_model(self) -> StyleGanModel:
        return self.stylegan_class(
            self.stylegan_method_options.model, self.stylegan_method_options
        )

    async def get_user_images(self) -> list:
        return await get_user_images_from_mongodb(self.mongodb, self.user.id)

    async def delete_user_images(self, deletion_options: DeletionOptions) -> None:
        if deletion_options.all_documents:
            image_id_list = [image.url for image in await self.get_user_images()]
            delete_blob_from_gcs("stylegan-images", image_id_list)
            delete_blob_from_gcs("stylegan-images-vectors", image_id_list)
            await delete_all_user_images_from_mongodb(self.mongodb, self.user.id)
        else:
            delete_blob_from_gcs("stylegan-images", deletion_options.id_list)
            delete_blob_from_gcs("stylegan-images-vectors", deletion_options.id_list)
            await delete_user_images_from_mongodb(
                self.mongodb, self.user.id, deletion_options.id_list
            )

    def generate_image(self) -> None:
        self.result_images_dict = self.stylegan_model.generate()

    def style_mix_images(self) -> None:
        row_image = self.get_seed_or_image_vector(
            self.stylegan_method_options.row_image
        )
        column_image = self.get_seed_or_image_vector(
            self.stylegan_method_options.column_image
        )

        self.result_images_dict = self.stylegan_model.style_mix(row_image, column_image)

    async def save_user_images(self) -> dict:
        for image_name, image_blobs in self.result_images_dict.items():
            image_blob, w_vector_blob = image_blobs
            if not (image_blob and w_vector_blob):
                self.result_images_dict[image_name] = (
                    self.stylegan_method_options.row_image
                    if image_name == "row_image"
                    else self.stylegan_method_options.column_image
                )
                continue
            image_id = upload_blob_to_gcs("stylegan-images", image_blob)
            upload_blob_to_gcs("stylegan-images-vectors", w_vector_blob, image_id)
            image_data = ImageData(
                url=image_id, auth0_id=self.user.id, method=self.stylegan_method_options
            )
            await save_user_image_in_mongodb(self.mongodb, image_data)
            self.result_images_dict[image_name] = image_id
        return self.result_images_dict

    @classmethod
    def get_class(cls) -> StyleGanUser:
        return cls

    @staticmethod
    def get_seed_or_image_vector(image_string: str) -> Union[int, bytes]:
        if image_string.isdigit():
            return int(image_string)
        else:
            return download_blob_from_gcs("stylegan-images-vectors", image_string)
