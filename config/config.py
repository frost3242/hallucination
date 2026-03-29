# -----------------------------
# DATA PATHS
# -----------------------------

DATA_LAKE_RAW = "data_lake/raw/"
DATA_LAKE_PROCESSED = "data_lake/processed/"

URL_DISCOVERY_FILE = "data/urls.json"
SCRAPED_DATA_FILE = "data/final_scraped_data.json"
PDF_STORAGE = "data/pdfs/"


# -----------------------------
# LLM CONFIGURATION
# -----------------------------

LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-4o"


# -----------------------------
# THRESHOLDS
# -----------------------------

SIMILARITY_THRESHOLD = 0.4
PLI_THRESHOLD = 0.5
OCI_THRESHOLD = 0.85


# -----------------------------
# FINAL RISK SCORE WEIGHTS
# -----------------------------

OCI_WEIGHT = 0.50
PLI_WEIGHT = 0.30
RELEVANCE_WEIGHT = 0.20


# -----------------------------
# FINAL RISK CLASSIFICATION
# -----------------------------

HIGH_RISK_THRESHOLD = 0.70
MEDIUM_RISK_THRESHOLD = 0.40


# -----------------------------
# CRAWLER SETTINGS
# -----------------------------

START_URLS = [
    "https://www.fda.gov",
    "https://www.nih.gov",
    "https://clinicaltrials.gov",
    "https://www.cdc.gov",
    "https://www.who.int",
    "https://pubmed.ncbi.nlm.nih.gov",
    "https://medlineplus.gov",
    "https://www.nhs.uk",
    "https://www.mayoclinic.org",
    "https://www.medscape.com"  # Added protected clinical database for testing
]

MAX_DEPTH = 3
MAX_PAGES = 500


# -----------------------------
# LOGIN CONFIGURATION
# -----------------------------

LOGIN_CREDENTIALS = {
    # The crawler will automatically detect this domain and inject these credentials into the DOM
    "https://www.medscape.com": {
        "username": "YOUR_MEDSCAPE_EMAIL_HERE",
        "password": "YOUR_MEDSCAPE_PASSWORD_HERE"
    }
}

# -----------------------------
# API KEYS
# -----------------------------
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", None)