import uuid

from google.cloud import storage


def upload_blob_to_gcs(
    bucket_name: str, image_blob: bytes, image_id: str = None
) -> str:
    """Upload a byte object to a google cloud stroage bucket.

    Args:
        bucket_name (str): the name of the gcs bucket
        image_blob (bytes): the image bytes object
        image_id (str, optional): the id, which will be the name in the bucket (creates a new one if None). Defaults to None.

    Returns:
        str: the id of the blob
    """
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
    """Download a byte object from a google cloud storage bucket.

    Args:
        bucket_name (str): the name of the gcs bucket
        image_id (str): the id, which will be the name in the bucket

    Returns:
        bytes: the downloaded byte object
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(image_id)
    image_blob = blob.download_as_bytes()

    return image_blob


def delete_blob_from_gcs(bucket_name: str, image_id_list: list) -> None:
    """Deletes multiple byte objects from a google cloud storage bucket.

    Args:
        bucket_name (str): the name of the gcs bucket
        image_id_list (list): a list of ids that should be deleted
    """
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    for image_id in image_id_list:
        blob = bucket.blob(image_id)
        blob.delete()
