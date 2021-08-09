from datetime import datetime
from typing import List

import pytz
from pydantic import BaseModel


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
