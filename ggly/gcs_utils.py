import json

from google.cloud import storage

client = storage.Client()


def upload_as_json(bucket: str, blob_name: str, o: str):
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(o), content_type='application/json')


def download_json(bucket: str, blob_name: str):
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(blob_name)
    metadata = blob.metadata
    return json.loads(blob.download_as_string()), metadata if metadata else {}


def update_metadata(bucket: str, blob_name: str, metadata: dict):
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(blob_name)
    blob.metadata = metadata
    blob.patch()


def upload(bucket, local_file_path, public=False):
    bucket = client.get_bucket(bucket)
    filename = local_file_path.split('/')[-1]
    blob = bucket.blob(filename)
    blob.upload_from_filename(local_file_path)
    if public:
        blob.make_public()
    return blob.public_url if public else None
