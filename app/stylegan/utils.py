from io import BytesIO
from typing import Any

import numpy as np
import PIL.Image
import torch


def seed_to_array_image(G, seed: int, truncation_psi: float) -> tuple:
    """Generate an image array and a feature vector of the image from a seed.

    Args:
        G ([type]): a loaded stylegan model
        seed (int): the seed for the generation
        truncation_psi (float): the truncation value for the generation

    Returns:
        tuple: the image array and the feature vector tensor
    """
    device = torch.device("cpu")

    z = torch.from_numpy(np.random.RandomState(int(seed)).randn(1, G.z_dim)).to(device)
    w = G.mapping(z, None, truncation_psi=truncation_psi, truncation_cutoff=8)

    image = w_vector_to_image(G, w)

    return image, w


def w_vector_to_image(G: Any, w: torch.Tensor) -> np.ndarray:
    """Generate an image array from a feature vector.

    Args:
        G (Any): a loaded stylegan model
        w (torch.Tensor): a feature vector

    Returns:
        np.ndarray: the image as a numpy array
    """
    noise_mode = "const"
    image = G.synthesis(w, noise_mode=noise_mode, force_fp32=True)
    image = (image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    image = image[0].cpu().numpy()
    return image


def save_image_as_bytes(image: np.ndarray) -> bytes:
    """Save an array image as bytes.

    Args:
        image (np.ndarray): the image array

    Returns:
        bytes: the image bytes object
    """
    buffer = BytesIO()
    PIL.Image.fromarray(image, "RGB").save(buffer, format="JPEG")
    return buffer.getvalue()


def save_vector_as_bytes(vector: torch.Tensor) -> bytes:
    """Save a tensor vector as bytes.

    Args:
        vector (torch.Tensor): the vector tensor

    Returns:
        bytes: the vector bytes object
    """
    buffer = BytesIO()
    torch.save(vector, buffer)
    return buffer.getvalue()


def load_vector_from_bytes(bytes_vector: bytes) -> torch.Tensor:
    """Load a vector from a bytes object.

    Args:
        bytes_vector (bytes): the bytes object of the vector

    Returns:
        torch.Tensor: the vector tensor
    """
    buffer = BytesIO(bytes_vector)
    return torch.load(buffer)
