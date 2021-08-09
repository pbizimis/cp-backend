import torch
import pickle
import os
import sys
from app.schemas.stylegan_models import Model
from typing import Any
import pathlib

sys.path.append(os.path.join(pathlib.Path().resolve(), "stylegan2_ada_pytorch"))


def load_model_from_pkl_stylegan2ada(folder_path: str, model: Model) -> Any:

    device = torch.device('cpu')

    with open(os.path.join(folder_path, model.filename), 'rb') as f:
        G = pickle.load(f)['G_ema'].to(device)

    return G