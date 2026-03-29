import os
import sys

# Ensure root directory is in pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import GCP_BUCKET_NAME

def get_client():
    try:
        from google.cloud import storage
        return storage.Client()
    except ImportError:
        print("google-cloud-storage is not installed. Skipping GCS sync.")
        return None
    except Exception as e:
        print(f"Failed to initialize GCP Storage Client: {e}")
        print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set in production.")
        return None

def download_from_gcs():
    if not GCP_BUCKET_NAME:
        return
        
    client = get_client()
    if not client: return
    
    bucket = client.bucket(GCP_BUCKET_NAME)
    blobs = bucket.list_blobs()
    
    print(f"\n[GCP SYNC] Downloading historical data from gs://{GCP_BUCKET_NAME}...")
    for blob in blobs:
        # Create local directory structure if it doesn't exist
        os.makedirs(os.path.dirname(blob.name), exist_ok=True)
        # Avoid downloading directories themselves
        if not blob.name.endswith("/"):
            blob.download_to_filename(blob.name)
            print(f"  Downloaded: {blob.name}")

def upload_to_gcs():
    if not GCP_BUCKET_NAME:
        return
        
    client = get_client()
    if not client: return
    
    bucket = client.bucket(GCP_BUCKET_NAME)
    
    # Sync the processed data, raw outputs, and the LLM golden dataset
    directories_to_sync = ["data", "data_lake", "evaluation/golden_data.json"]
    
    print(f"\n[GCP SYNC] Uploading new pipeline results to gs://{GCP_BUCKET_NAME}...")
    for path in directories_to_sync:
        if os.path.isfile(path):
            blob = bucket.blob(path.replace("\\", "/"))
            blob.upload_from_filename(path)
            print(f"  Uploaded: {path}")
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    local_path = os.path.join(root, file)
                    # Use forward slashes for GCP blob names
                    blob_name = local_path.replace("\\", "/")
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(local_path)
                    print(f"  Uploaded: {blob_name}")
                    
if __name__ == "__main__":
    # Test script locally
    upload_to_gcs()
