import random
import torch
import numpy as np
import PIL.Image
import base64
from io import BytesIO

def generate_stylegan2ada_images(model, generation_options: dict):

    bytes_io = BytesIO()
    G = model
    truncation_psi = generation_options.truncation

    latent = random.randint(0,2**32-1) # 2**32-1 is the highest value

    device = torch.device('cpu')

    images = []

    z = torch.from_numpy(np.random.RandomState(latent).randn(1, G.z_dim)).to(device)
    img = G(z, None, truncation_psi=truncation_psi, noise_mode="const", force_fp32=True)
    img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    final_image = PIL.Image.fromarray(img[0].cpu().numpy(), 'RGB')
    final_image.save(bytes_io, format="JPEG")
    
    image_blob = bytes_io.getvalue()

    return image_blob