import os
from google.cloud import storage
from firebase_admin import credentials

# Set up Firebase Storage client using the same credentials as firebase_admin
FIREBASE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', 'ice-cream-shop-69592.appspot.com')

# This assumes your GOOGLE_APPLICATION_CREDENTIALS env var is set, or you use the same key as firebase_admin

def upload_file_to_firebase_storage(local_file_path, destination_blob_name):
    """
    Uploads a file to Firebase Storage and returns the public URL.
    :param local_file_path: Path to the file on local disk
    :param destination_blob_name: Path in the storage bucket (e.g. 'ice_cream_images/filename.png')
    :return: Public URL of the uploaded file
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(FIREBASE_BUCKET)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    # Make the file publicly accessible
    blob.make_public()
    return blob.public_url
