import uuid
from io import BytesIO

import PIL.Image
import torch
from google.cloud import storage

from app.db.google_cloud_storage import delete_blob_from_gcs, download_blob_from_gcs, upload_blob_to_gcs


def test_google_cloud_storage():

    # make sure buckets are empty before testing
    storage_client = storage.Client()
    blobs = storage_client.list_blobs("cp-testing-image")
    delete_blob_from_gcs("cp-testing-image", [blob.name for blob in list(blobs)])

    blobs = storage_client.list_blobs("cp-testing-vector")
    delete_blob_from_gcs("cp-testing-vector", [blob.name for blob in list(blobs)])

    # access mock bytes (generated beforehand by this application)
    with open(
        "tests/unit_tests/test_stylegan/assertion_files/save_image_as_bytes_assertion_result.txt",
        "rb",
    ) as f:
        image_bytes = f.read()

    # create an image object
    pil_image = PIL.Image.open(BytesIO(image_bytes)).convert("RGB")

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/save_vector_as_bytes_assertion_result.txt",
        "rb",
    ) as f:
        vector_bytes = f.read()

    # create an tensor object
    vector_tensor = torch.load(BytesIO(vector_bytes))

    # upload bytes
    image_id = upload_blob_to_gcs("cp-testing-image", image_bytes)
    assert uuid.UUID(image_id, version=4)

    # upload bytes to another bucket
    vector_id = upload_blob_to_gcs("cp-testing-vector", vector_bytes, image_id)
    assert uuid.UUID(image_id, version=4)

    # assert that both have the same id since it is passed to the second function call
    assert image_id == vector_id

    # download bytes
    downloaded_image_bytes = download_blob_from_gcs("cp-testing-image", image_id)
    downloaded_pil_image = PIL.Image.open(BytesIO(downloaded_image_bytes)).convert(
        "RGB"
    )

    downloaded_vector_bytes = download_blob_from_gcs("cp-testing-vector", vector_id)
    downloaded_vector_tensor = torch.load(BytesIO(downloaded_vector_bytes))

    # assert that bytes equal the previous bytes by loading them as an image and tensor
    assert list(pil_image.getdata()) == list(downloaded_pil_image.getdata())
    assert torch.equal(vector_tensor, downloaded_vector_tensor)

    # delete the bytes from the buckets
    delete_blob_from_gcs("cp-testing-image", [image_id])
    delete_blob_from_gcs("cp-testing-vector", [vector_id])

    # list them to ensure that everything is cleaned up and the deletion worked
    storage_client = storage.Client()
    blobs = storage_client.list_blobs("cp-testing-image")

    assert len(list(blobs)) == 0
    blobs = storage_client.list_blobs("cp-testing-vector")
    assert len(list(blobs)) == 0
