from pydantic import BaseModel
from datetime import datetime
import pytz
from typing import List

class Image(BaseModel):
    url: str
    auth0_id: str
    creation_date: datetime = datetime.now(pytz.timezone("Europe/Berlin"))
    method: dict

class DeletionOptions(BaseModel):
    all_documents: bool = False
    id_list: List[str]