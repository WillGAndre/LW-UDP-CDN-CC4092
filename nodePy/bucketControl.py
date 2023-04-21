import os
from google.cloud import storage

class Bucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "asc-project-378811-07d7c84611e8.json"

        project_id = "asc-project-378811"
        bucket_name = "bucket01_acs-project"

        storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)
    # List all objects in the bucket
    def list(self):
        print(f"Objects in bucket {bucket_name}:")
        for blob in bucket.list_blobs():
            print(f" - {blob.name}")

    # Upload a new object to the bucket
    def insert(self, file_path):
        blob_name = os.path.basename(file_path)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {bucket_name} as {blob_name}.")

    # Download an object from the bucket
    def get(self, blob_name, destination_path):
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)
        print(f"File {blob_name} downloaded from {bucket_name} to {destination_path}.")

    # Delete an object from the bucket
    def delete(self, blob_name):
        blob = bucket.blob(blob_name)
        blob.delete()
        print(f"File {blob_name} deleted from {bucket_name}.")

