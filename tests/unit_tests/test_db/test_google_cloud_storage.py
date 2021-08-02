from app.db.google_cloud_storage import upload_blob, download_blob
import uuid

def test_upload_blob(mocker):

    class Blob():

        call_content_type_values = []

        def __init__(self, image_id):
            self.bucket_name = image_id

        def upload_from_string(self, image, content_type):
            self.call_content_type_values.append(content_type)

    class Bucket():
        def __init__(self, bucket_name):
            self.bucket_name = bucket_name

        def blob(self, image_id):
            return Blob(image_id)

    class Client():
        def bucket(self, bucket_name):
            return Bucket(bucket_name)

    mocker.patch("app.db.google_cloud_storage.storage.Client", return_value=Client())

    image_id = upload_blob("bucket_name", "image_string", "image_id")
    
    assert image_id == "image_id"
    assert Blob.call_content_type_values[0] == "application/octet-stream"

    image_id = upload_blob("bucket_name", "image_string")
    
    assert uuid.UUID(image_id, version=4)
    assert Blob.call_content_type_values[1] == "image/jpeg"

def test_download_blob(mocker):

    class Blob():

        def __init__(self, image_id):
            self.bucket_name = image_id

        def download_as_bytes(self):
            return "bytes_image"

    class Bucket():
        def __init__(self, bucket_name):
            self.bucket_name = bucket_name

        def blob(self, image_id):
            return Blob(image_id)

    class Client():
        def bucket(self, bucket_name):
            return Bucket(bucket_name)

    mocker.patch("app.db.google_cloud_storage.storage.Client", return_value=Client())

    image_blob = download_blob("bucket_name", "image_id")
    
    assert image_blob == "bytes_image"