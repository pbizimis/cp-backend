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
    """A class that describes a user that uses a certain stylegan version with a model and methods."""

    def __init__(
        self,
        user: Auth0User,
        mongodb: AsyncIOMotorClient,
        stylegan_class: Type[StyleGanModel] = None,
        stylegan_method_options: dict = None,
    ) -> None:
        """Init a new stylegan user

        Args:
            user (Auth0User): the current user object (decoded JWT)
            mongodb (AsyncIOMotorClient): the mongodb database connection
            stylegan_class (Type[StyleGanModel], optional): the class of the stylegan version that the user should use. Defaults to None.
            stylegan_method_options (dict, optional): a dict that contains the options for a specific method. Defaults to None.
        """
        self.user = user
        self.stylegan_method_options = stylegan_method_options
        self.stylegan_class = stylegan_class
        self.mongodb = mongodb
        if self.stylegan_class:
            self.stylegan_model = self._load_stylegan_model()

    def _load_stylegan_model(self) -> StyleGanModel:
        """Create a new object of the stylegan class that the user should use."""
        return self.stylegan_class(
            self.stylegan_method_options.model, self.stylegan_method_options
        )

    async def get_user_images(self) -> list:
        """Get a all images of a user from mongodb."""
        return await get_user_images_from_mongodb(self.mongodb, self.user.id)

    async def delete_user_images(self, deletion_options: DeletionOptions) -> None:
        """Delete user images from mongodb and google cloud storage.

        Args:
            deletion_options (DeletionOptions): an object that contains the options for deletion (a list of ids or a specifier for all images)
        """
        if deletion_options.all_documents:
            # Delete all user image data from mongodb and gcs
            image_id_list = [image.url for image in await self.get_user_images()]
            delete_blob_from_gcs("stylegan-images", image_id_list)
            delete_blob_from_gcs("stylegan-images-vectors", image_id_list)
            await delete_all_user_images_from_mongodb(self.mongodb, self.user.id)
        else:
            # Delete a list of user image data from mongodb and gcs
            delete_blob_from_gcs("stylegan-images", deletion_options.id_list)
            delete_blob_from_gcs("stylegan-images-vectors", deletion_options.id_list)
            await delete_user_images_from_mongodb(
                self.mongodb, self.user.id, deletion_options.id_list
            )

    def generate_image(self) -> None:
        """Generate a new image with the specified stylegan version and model."""
        self.result_images_dict = self.stylegan_model.generate()

    def style_mix_images(self) -> None:
        """Style mix two images with the specified stylegan version and model."""
        row_image = self.get_seed_or_image_vector(
            self.stylegan_method_options.row_image
        )
        column_image = self.get_seed_or_image_vector(
            self.stylegan_method_options.column_image
        )

        self.result_images_dict = self.stylegan_model.style_mix(row_image, column_image)

    async def save_user_images(self) -> dict:
        """Save user image data in mongodb and google cloud storage."""
        for image_name, image_blobs in self.result_images_dict.items():
            image_blob, w_vector_blob = image_blobs
            # If image_blob and w_vector_blob are None, both have been passed in as already created (pulled from GCS with their id).
            # Therefore, the result dict can be set to the initial id (either row or column image id).
            if not (image_blob and w_vector_blob):
                self.result_images_dict[image_name] = (
                    self.stylegan_method_options.row_image
                    if image_name == "row_image"
                    else self.stylegan_method_options.column_image
                )
                continue
            # If not, the image needs to be uploaded to GCS and its data saved to mongodb
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
        """Return the StyleGanUser class (for fastapi dependencies)."""
        return cls

    @staticmethod
    def get_seed_or_image_vector(image_string: str) -> Union[int, bytes]:
        """Validate an input image string as an int or download the corresponding vector from google cloud storage."""
        if image_string.isdigit():
            return int(image_string)
        else:
            return download_blob_from_gcs("stylegan-images-vectors", image_string)
