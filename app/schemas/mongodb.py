from datetime import datetime
from typing import List

import pytz
from pydantic import BaseModel


class ImageData(BaseModel):
    url: str
    auth0_id: str
    creation_date: datetime = datetime.now(pytz.timezone("Europe/Berlin"))
    method: dict


class DeletionOptions(BaseModel):
    all_documents: bool = False
    id_list: List[str]
