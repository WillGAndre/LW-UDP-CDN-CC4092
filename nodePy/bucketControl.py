import os
from google.cloud import storage

class Bucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "accountCreds.json"

        self.project_id = "asc23-378811"
        self.bucket_name = "bucketasc"
        
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(self.bucket_name)

    # List all objects in the bucket
    def list(self):
        print(f"Objects in bucket {self.bucket_name}:")
        for blob in self.bucket.list_blobs():
            print(f" - {blob.name}")

    # Upload a new object to the bucket
    def insert(self, file_path):
        blob_name = os.path.basename(file_path)
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {self.bucket_name} as {blob_name}.")

    # Download an object from the bucket
    def get(self, blob_name, destination_path):
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination_path)
        print(f"File {blob_name} downloaded from {self.bucket_name} to {destination_path}.")

    # Delete an object from the bucket
    def delete(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()
        print(f"File {blob_name} deleted from {self.bucket_name}.")

if __name__ == "__main__":

    bk = Bucket()
    bk.list()
