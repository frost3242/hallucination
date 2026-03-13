import os
import sys

# Ensure base directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.crawler import crawl
from ingestion.api_collector import fetch_api
from processing.normalization import normalize


RAW_PATH = "data_lake/raw/openfda_drugs"
PROCESSED_PATH = "data_lake/processed/openfda_drugs"


def run_pipeline():

    print("Starting Data Pipeline\n")

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

    for file in os.listdir(RAW_PATH):

        if file.endswith(".json"):

            input_path = os.path.join(RAW_PATH, file)

            df = normalize(input_path)

            output_file = file.replace(".json", ".csv")
            output_path = os.path.join(PROCESSED_PATH, output_file)

            df.to_csv(output_path, index=False)

            print("Saved normalized →", output_path)

    print("Normalization complete\n")

    print("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()