import uuid

from google.cloud import storage


def upload_blob_to_gcs(bucket_name: str, image_blob: bytes, image_id: str = None):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not image_id:
        image_id = uuid.uuid4().hex
        content_type = "image/jpeg"
    else:
        content_type = "application/octet-stream"
    blob = bucket.blob(image_id)

    blob.upload_from_string(image_blob, content_type=content_type)

    return image_id


def download_blob_from_gcs(bucket_name: str, image_id: str) -> bytes:

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(image_id)
    image_blob = blob.download_as_bytes()

    return image_blob


def delete_blob_from_gcs(bucket_name: str, image_id_list: list) -> None:

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    for image_id in image_id_list:
        blob = bucket.blob(image_id)
        blob.delete()
