import os
import sys

# Ensure base directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.crawler import crawl
from ingestion.api_collector import fetch_api
from processing.normalization import normalize
from processing.deduplication import deduplicate_sources
from processing.source_ranker import rank_sources
from pipeline.active_learning import generate_active_learning_samples
from utils.gcp_sync import download_from_gcs, upload_to_gcs


RAW_PATH = "data_lake/raw/openfda_drugs"
PROCESSED_PATH = "data_lake/processed/openfda_drugs"


def run_pipeline():

    print("Starting Data Pipeline\n")

    # Sync historical data from cloud storage before overwriting locally
    download_from_gcs()

    os.makedirs(RAW_PATH, exist_ok=True)
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    # -----------------------------
    # STEP 1 — API COLLECTION
    # -----------------------------

    print("STEP 1 — API collection")

    api_sources = {
        "openfda_drugs": "https://api.fda.gov/drug/label.json?limit=5"
    }

    for name, url in api_sources.items():
        fetch_api(url, name)

    print("API collection done\n")

    # -----------------------------
    # STEP 2 — WEB CRAWLING
    # -----------------------------

    print("STEP 2 — Crawling")

    # crawler internally uses START_URLS from config
    crawl()

    print("Crawling done\n")

    # -----------------------------
    # STEP 3 — NORMALIZATION
    # -----------------------------

    print("STEP 3 — Normalization")

    # Gather data from both API responses and the Web Crawler
    files_to_process = []
    
    # 1. Add API files
    if os.path.exists(RAW_PATH):
        for file in os.listdir(RAW_PATH):
            if file.endswith(".json"):
                files_to_process.append(os.path.join(RAW_PATH, file))
                
    # 2. Add Crawler output file
    if os.path.exists("data/final_scraped_data.json"):
        files_to_process.append("data/final_scraped_data.json")

    for input_path in files_to_process:
        file_basename = os.path.basename(input_path)

        # 1. Normalize
        df = normalize(input_path)
        
        output_file = file_basename.replace(".json", ".csv")
        output_path = os.path.join(PROCESSED_PATH, output_file)

        if not df.empty:
            # 2. Deduplicate
            df = deduplicate_sources(df)

            # 3. Handle scoring/ranking (Mocking access type for ranker if missing)
            if "access_type" not in df.columns:
                df["access_type"] = "API" if "api" in file_basename else "WEB"
            
            # Save temp file for ranker (since rank_sources currently expects a filepath)
            temp_csv = output_path.replace(".csv", "_unranked.csv")
            df.to_csv(temp_csv, index=False)
            
            # Rank
            df = rank_sources(temp_csv)
            os.remove(temp_csv)

        df.to_csv(output_path, index=False)

        print("Saved normalized & ranked →", output_path)

    print("Normalization & Post-Processing complete\n")

    # -----------------------------
    # STEP 4 — ACTIVE LEARNING
    # -----------------------------

    print("STEP 4 — Active Learning Synthetic Generation")

    for file in os.listdir(PROCESSED_PATH):
        if file.endswith(".csv"):
            processed_csv = os.path.join(PROCESSED_PATH, file)
            # Sample 2 hard cases per processed dataset
            generate_active_learning_samples(processed_csv, samples=2)

    print("Active Learning phase complete\n")

    # Push all updated datasets to Google Cloud bucket
    upload_to_gcs()

    print("\nPipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()