from pydantic import BaseModel
from datetime import datetime
import pytz
from typing import List

class User(BaseModel):
    auth0_id: str
    total_images: int
    creation_date: datetime = datetime.now(pytz.timezone("Europe/Berlin"))
    recent_images: List[str]

class Image(BaseModel):
    url: str
    auth0_id: str
    creation_date: datetime = datetime.now(pytz.timezone("Europe/Berlin"))
    stylegan_data: dict