from io import BytesIO
import PIL.Image
import torch
import numpy as np
from typing import Any

def seed_to_array_image(G, seed: int, truncation_psi: float) -> tuple:
    device = torch.device('cpu')

    z = torch.from_numpy(np.random.RandomState(int(seed)).randn(1, G.z_dim)).to(device)
    w = G.mapping(z, None, truncation_psi=truncation_psi, truncation_cutoff=8)
    
    image = w_vector_to_image(G, w)

    return image, w

def w_vector_to_image(G: Any, w: torch.Tensor) -> np.ndarray:
    noise_mode = "const"
    image = G.synthesis(w, noise_mode=noise_mode, force_fp32=True)
    image = (
        (image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    )
    image = image[0].cpu().numpy()
    return image

def save_image_as_bytes(image: np.ndarray) -> bytes:
    buffer = BytesIO()
    PIL.Image.fromarray(image, "RGB").save(buffer, format="JPEG")
    return buffer.getvalue()

def save_vector_as_bytes(vector: torch.Tensor) -> bytes:
    buffer = BytesIO()
    torch.save(vector, buffer)
    return buffer.getvalue()

def load_bytes_vector(bytes_vector: bytes) -> torch.Tensor:
    buffer = BytesIO(bytes_vector)
    return torch.load(buffer)