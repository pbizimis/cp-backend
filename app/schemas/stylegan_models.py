from __future__ import annotations
import os
import re
from dataclasses import dataclass
from pydantic import BaseModel
from abc import ABC
from typing import Optional

class StyleGanModel(ABC):
    pass

class Model(BaseModel):
    img: int
    res: int
    fid: int
    version: Optional[str]

    @property
    def filename(self) -> str:
        return f"img{self.img}res{self.res}fid{self.fid}.pkl"

    @classmethod
    def from_filename(cls, filename: str, version: str) -> Model:
        matcher = re.compile(r"img(?P<img>\d*)res(?P<res>\d*)fid(?P<fid>\d*)")
        if m := matcher.match(filename):
            return cls(
                img=int(m.group("img")), 
                res=int(m.group("res")), 
                fid=int(m.group("fid")),
                version=version[:-8] # [:-8] eliminates '_models/' from root path string
            )

    def __hash__(self) -> int:                                                         
        return hash((type(self),) + tuple(self.__dict__.values()))      

class Models():

    def __init__(self, path: str) -> None:
        self.path = path
        self.models = self.create_models()

    def __call__(self) -> list:
        return self.models

    def create_models(self) -> list:
        return [Model.from_filename(filename, self.path) for filename in os.listdir(self.path)]

stylegan2_ada_models = Models("stylegan2_ada_models/")