from io import BytesIO
import PIL.Image
import torch
import numpy as np

def seeds_to_array_images(G, seeds, truncation_psi):
    device = torch.device('cpu')
    noise_mode = "const"

    all_z = np.stack(
            [np.random.RandomState(seed).randn(G.z_dim) for seed in seeds]
        )
    all_w = G.mapping(torch.from_numpy(all_z).to(device), None)

    w_avg = G.mapping.w_avg
    all_w = w_avg + (all_w - w_avg) * truncation_psi

    seed_images = G.synthesis(all_w, noise_mode=noise_mode, force_fp32=True)
    seed_images = (seed_images.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8).cpu().numpy()

    return seed_images, all_w

def seed_to_array_image(G, seed, truncation_psi):
    device = torch.device('cpu')

    z = torch.from_numpy(np.random.RandomState(int(seed)).randn(1, G.z_dim)).to(device)
    w = G.mapping(z, None, truncation_psi=truncation_psi, truncation_cutoff=8)
    
    image = w_vector_to_image(G, w)

    return image, w

def w_vector_to_image(G, w):
    noise_mode = "const"
    image = G.synthesis(w, noise_mode=noise_mode, force_fp32=True)
    image = (
        (image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    )
    image = image[0].cpu().numpy()
    return image

def save_image_as_bytes(image):
    buffer = BytesIO()
    PIL.Image.fromarray(image, "RGB").save(buffer, format="JPEG")
    return buffer.getvalue()

def save_vector_as_bytes(vector):
    buffer = BytesIO()
    torch.save(vector, buffer)
    return buffer.getvalue()

def load_bytes_vector(bytes_vector):
    buffer = BytesIO(bytes_vector)
    return torch.load(buffer)