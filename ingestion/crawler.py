# ingestion/crawler.py

import json
import requests
import os
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

from config.config import APIFY_TOKEN, START_URLS

# -----------------------------
# PATHS
# -----------------------------

DATA_DIR = "data"
URLS_FILE = f"{DATA_DIR}/urls.json"
PDF_DIR = f"{DATA_DIR}/pdfs"
FINAL_SCRAPED_FILE = f"{DATA_DIR}/final_scraped_data.json"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# -----------------------------
# URL DISCOVERY
# -----------------------------

def discover_urls(start_urls, max_links=500):

    discovered = set()

    for url in start_urls:

        print(f"\nDiscovering links from {url}")

        try:

            r = requests.get(url, timeout=20)

            soup = BeautifulSoup(r.text, "html.parser")

            for link in soup.find_all("a", href=True):

                href = link["href"]

                if href.startswith("http"):

                    discovered.add(href)

                    if len(discovered) >= max_links:
                        break

        except Exception as e:
            print("Discovery error:", e)

    urls = list(discovered)

    with open(URLS_FILE, "w") as f:
        json.dump(urls, f, indent=2)

    print(f"\nTotal discovered URLs: {len(urls)}")

    return urls


# -----------------------------
# PDF DOWNLOAD
# -----------------------------

def download_pdf(url):

    try:

        filename = url.split("/")[-1]

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        filepath = os.path.join(PDF_DIR, filename)

        r = requests.get(url, timeout=30)

        with open(filepath, "wb") as f:
            f.write(r.content)

        return filepath

    except Exception as e:

        print("PDF download error:", e)

        return None


# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------

def extract_pdf_text(pdf_path):

    try:

        text = extract_text(pdf_path)

        return text

    except Exception as e:

        print("PDF extraction error:", e)

        return ""


# -----------------------------
# APIFY SCRAPER
# -----------------------------

def crawl_with_apify(urls):

    endpoint = f"https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {

        "startUrls": [{"url": u} for u in urls[:50]],

        "maxRequestsPerCrawl": 500,

        "linkSelector": "a[href]",

        "pseudoUrls": [
            {"purl": "https://[.*]"}
        ],

        "pageFunction": """
        async function pageFunction(context) {

            const { request, $, enqueueLinks } = context;

            await enqueueLinks({
                selector: "a[href]",
                strategy: "same-domain"
            });

            const text = $("body").text();

            return {
                url: request.url,
                title: $("title").text(),
                text: text
            };
        }
        """
    }

    try:

        response = requests.post(endpoint, json=payload, timeout=600)

        data = response.json()

        print(f"\nTotal pages scraped: {len(data)}")

        return data

    except Exception as e:

        print("Apify error:", e)

        return []


# -----------------------------
# PDF EXTRACTION FROM URL LIST
# -----------------------------

def process_pdfs(urls):

    pdf_data = []

    for url in urls:

        if ".pdf" in url.lower():

            print(f"\nDownloading PDF: {url}")

            pdf_path = download_pdf(url)

            if pdf_path:

                text = extract_pdf_text(pdf_path)

                pdf_data.append({

                    "url": url,
                    "title": os.path.basename(pdf_path),
                    "text": text

                })

    print(f"\nTotal PDFs processed: {len(pdf_data)}")

    return pdf_data


# -----------------------------
# MAIN PIPELINE
# -----------------------------

def crawl():

    print("\nSTEP 1 — URL Discovery")

    urls = discover_urls(START_URLS)

    print("\nSTEP 2 — HTML Crawling")

    html_data = crawl_with_apify(urls)

    print("\nSTEP 3 — PDF Extraction")

    pdf_data = process_pdfs(urls)

    all_data = html_data + pdf_data

    with open(FINAL_SCRAPED_FILE, "w", encoding="utf-8") as f:

        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\nFinal dataset saved → {FINAL_SCRAPED_FILE}")

    return all_data


# -----------------------------
# LOCAL TEST
# -----------------------------

if __name__ == "__main__":

    crawl()