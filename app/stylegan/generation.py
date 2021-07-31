import random
import torch
import numpy as np
import PIL.Image
import base64
from io import BytesIO
from app.stylegan.utils import save_image_as_bytes, save_vector_as_bytes

def seed_to_array_image(G, seed, truncation_psi):
    device = torch.device('cpu')

    z = torch.from_numpy(np.random.RandomState(int(seed)).randn(1, G.z_dim)).to(device)
    w = G.mapping(z, None, truncation_psi=truncation_psi, truncation_cutoff=8)
    img = G.synthesis(w, noise_mode='const', force_fp32=True)

    img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    img = img[0].cpu().numpy()

    return img, w

def generate_stylegan2ada_images(model, generation_options: dict):

    G = model
    truncation_psi = generation_options.truncation
    seed = generation_options.seed

    if not seed:
        seed = random.randint(0,2**32-1) # 2**32-1 is the highest value

    img, w = seed_to_array_image(G, seed, truncation_psi)

    image_blob = save_image_as_bytes(img)
    w_blob = save_vector_as_bytes(w)

    return {"result_image": (image_blob, w_blob)}