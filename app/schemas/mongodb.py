from datetime import datetime
from typing import List
import uuid

from pydantic import validator

import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel


class MongoClient:
    """The MongoDB client class."""

    def __init__(self):
        self.client = AsyncIOMotorClient()

    # Get method for FastAPI dependency injection
    def get_client(self):
        return self.client


class ImageData(BaseModel):
    """A pydantic class for image data.

    Attributes:
        url (str): the id of the image data
        auth0_id (str): the auth0 id of the user
        creation_date (datetime): the creation time. Defaults to datetime.now(pytz.timezone("Europe/Berlin").
        method (dict): the creation method of the image
    """

    url: str
    auth0_id: str
    creation_date: datetime = datetime.now(pytz.timezone("Europe/Berlin"))
    method: dict


class DeletionOptions(BaseModel):
    """A pydantic class for deletion options.

    Attributes:
        all_documents (bool): a bool if all mongodb documents of a user should be deleted. Defaults to False
        id_list (List[str]): a list of id strings
    """

    all_documents: bool = False
    id_list: List[str]

    @validator("id_list")
    def id_list_elements_are_id(cls, id_list):
        """Validate that the elements of the given list are valid v4 uuids."""
        try:
            for image_id in id_list:
                if uuid.UUID(image_id, version=4):
                    continue
                else:
                    raise ValueError("Please give a list of valid image ids.")
            return id_list
        except:
            raise ValueError("Please give a list of valid image ids.")
