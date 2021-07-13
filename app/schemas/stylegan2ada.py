from pydantic import BaseModel

class Options(BaseModel):
    @classmethod
    def get_schema(cls):
        return cls.schema()

class GenerationOptions(Options):
    model: str
    truncation: float

class StyleMixOptions(Options):
    model: str
    images: list