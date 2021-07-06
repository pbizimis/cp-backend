from pydantic import BaseModel

class GenerationOptions(BaseModel):
    model: str
    truncation: float

class StyleMixOptions(BaseModel):
    model: str
    images: list