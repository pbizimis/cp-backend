from __future__ import annotations

import os
import re
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class StyleGanModel(ABC):
    """An abstract base class for stylegan models (for type hiting)."""

    pass


class Model(BaseModel):
    """A pydantic class for stylegan pkl file models.

    Attributes:
        img (int): the amount of images used to train the model
        res (int): the resolution of the training data
        fid (int): the FID (Fréchet Inception Distance)
        version (Optional[str]): an optional string containing the version of the model
    """

    img: int
    res: int
    fid: int
    version: Optional[str]

    @property
    def filename(self) -> str:
        """Return the filename of the model based on its attributes."""
        return f"img{self.img}res{self.res}fid{self.fid}.pkl"

    @classmethod
    def from_filename(cls, filename: str, version: str) -> Model:
        """Create a new model from a filename and a version.

        Args:
            filename (str): the filename of the pkl model
            version (str): the version of the pkl model

        Returns:
            Model: a new model object
        """
        matcher = re.compile(r"img(?P<img>\d*)res(?P<res>\d*)fid(?P<fid>\d*)")
        if m := matcher.match(filename):
            return cls(
                img=int(m.group("img")),
                res=int(m.group("res")),
                fid=int(m.group("fid")),
                version=version[
                    :-8
                ],  # [:-8] eliminates '_models/' from root path string
            )

    def __hash__(self) -> int:
        """Hash the object to enable the usage of the object as a dict key."""
        return hash((type(self),) + tuple(self.__dict__.values()))


class ModelCollection:
    """A class that describes a collection of models."""

    def __init__(self, path: str) -> None:
        """Init a new model collection.

        Args:
            path (str): the path to the model collection folder
        """
        self.path = path
        self.models = self.create_models()

    def __call__(self) -> list:
        """Return the list of models in the collection."""
        return self.models

    def create_models(self) -> list:
        """Create list of models from the collection path."""
        return [
            Model.from_filename(filename, self.path)
            for filename in os.listdir(self.path)
        ]


stylegan2ada_models = ModelCollection("stylegan2_ada_models/")
