import os
import json
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

import os
import sys

# Ensure root directory is in pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

from config.config import START_URLS, MAX_PAGES, LOGIN_CREDENTIALS

# -----------------------------
# PATHS
# -----------------------------
DATA_DIR = "data"
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
FINAL_SCRAPED_FILE = os.path.join(DATA_DIR, "final_scraped_data.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# -----------------------------
# AUTONOMOUS AGENT CRAWLER
# -----------------------------
def crawl():
    print("\nSTEP 1 — Launching Autonomous Playwright Agent")
    all_data = []
    
    with sync_playwright() as p:
        # Launch Chromium headless with Cloud/Docker disabled sandboxing
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        context = browser.new_context()
        page = context.new_page()

        # Execute Autonomous Logins over protected domains
        if LOGIN_CREDENTIALS:
            print("\nSTEP 2 — Bypassing Untapped Protected Sources")
            for domain, creds in LOGIN_CREDENTIALS.items():
                print(f"Injecting credentials for {domain}...")
                try:
                    page.goto(domain, timeout=20000)
                    
                    # Automatically find standard login fields (heuristics)
                    if page.locator("input[type='password']").count() > 0:
                        page.fill("input[type='text'], input[type='email']", creds.get("username", ""))
                        page.fill("input[type='password']", creds.get("password", ""))
                        
                        # Click the first submit button we can find
                        page.locator("button[type='submit'], input[type='submit']").first.click()
                        page.wait_for_load_state("networkidle")
                        print(f"Successfully authenticated into {domain}")
                except Exception as e:
                    print(f"Login bypass failed for {domain}: {e}")

        print("\nSTEP 3 — Deep HTML & PDF Crawling")
        visited = set()
        queue = list(START_URLS)
        
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            
            print(f"Scraping -> {url}")
            visited.add(url)
            
            try:
                # Handle direct PDF downloads
                if url.endswith(".pdf"):
                    filename = url.split("/")[-1]
                    if not filename.endswith(".pdf"):
                        filename += ".pdf"
                        
                    filepath = os.path.join(PDF_DIR, filename)
                    r = requests.get(url, timeout=30)
                    with open(filepath, "wb") as f:
                        f.write(r.content)
                        
                    text = extract_text(filepath)
                    if text.strip():
                        all_data.append({
                            "url": url, 
                            "title": filename, 
                            "text": text
                        })
                
                # Handle Javascript-rendered Web Pages
                else:
                    page.goto(url, timeout=20000, wait_until="networkidle")
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text(separator=' ', strip=True)
                    
                    if text.strip():
                        all_data.append({
                            "url": url, 
                            "title": page.title() or url, 
                            "text": text
                        })
                    
                    # Discover more links dynamically to keep exploring
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith("http") and href not in visited:
                            # Keep crawler scoped roughly to our starting hubs
                            if any(domain in href for domain in START_URLS):
                                queue.append(href)
                                
            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        # Teardown the headless browser safely
        browser.close()

    print(f"\nSTEP 4 — Saving Dataset")
    with open(FINAL_SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"Final dataset aggregated → {FINAL_SCRAPED_FILE}")
    print(f"Total Unique Sources Extracted: {len(all_data)}")
    
    return all_data

if __name__ == "__main__":
    crawl()