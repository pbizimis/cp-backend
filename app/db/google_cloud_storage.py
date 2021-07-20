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
