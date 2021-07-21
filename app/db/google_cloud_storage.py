from google.cloud import storage
import uuid


def upload_blob(bucket_name, image):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    image_id = uuid.uuid4().hex
    blob = bucket.blob(image_id)

    blob.upload_from_string(image, content_type="image/jpeg")

    return image_id

def download_blob(bucket_name: str, image_ids: list) -> list:
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    image_blobs = []

    for image_id in image_ids:
        blob = bucket.blob(image_id)
        image_blobs.append(blob.download_as_bytes())

    return image_blobs

