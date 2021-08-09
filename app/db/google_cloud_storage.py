from google.cloud import storage
import uuid


def upload_blob(bucket_name: str, image: bytes, image_id: str = None):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not image_id:
        image_id = uuid.uuid4().hex
        content_type = "image/jpeg"
    else:
        content_type = "application/octet-stream"
    blob = bucket.blob(image_id)

    blob.upload_from_string(image, content_type=content_type)

    return image_id

def download_blob(bucket_name: str, image_id: str) -> bytes:
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(image_id)
    image_blob = blob.download_as_bytes()

    return image_blob

def delete_blob(bucket_name: str, image_ids: list) -> None:

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    for image_id in image_ids:
        blob = bucket.blob(image_id)
        blob.delete()