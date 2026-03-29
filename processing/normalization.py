import json
import pandas as pd
import os
import re
import spacy

from config.config import SCRAPED_DATA_FILE, DATA_LAKE_PROCESSED

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

OUTPUT_FILE = os.path.join(DATA_LAKE_PROCESSED, "knowledge_base/data.csv")

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text):
    """
    Accurately splits text into sentences using spaCy, avoiding regex pitfalls 
    with medical abbreviations (e.g. Dr., mg.).
    """
    doc = nlp(text)
    
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 30]

    return sentences


def normalize(json_file=SCRAPED_DATA_FILE):

    print("\nStarting normalization")

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    # Automatically map OpenFDA json blocks to standard crawler schema
    if isinstance(data, dict) and "results" in data:
        parsed_data = []
        for result in data["results"]:
            text_blocks = []
            for key, val in result.items():
                if isinstance(val, list) and val and isinstance(val[0], str):
                    text_blocks.append(val[0])
            parsed_data.append({
                "url": "https://api.fda.gov/drug/label",
                "title": "OpenFDA API Record",
                "text": " ".join(text_blocks)
            })
        data = parsed_data
    elif isinstance(data, dict):
        data = [data]

    rows = []

    for item in data:

        url = item.get("url", "")
        title = clean_text(item.get("title", ""))
        text = clean_text(item.get("text", ""))

        if not text:
            continue

        sentences = split_sentences(text)

        for sent in sentences:

            rows.append({

                "title": title,
                "evidence_sentence": sent,
                "source_url": url,
                "confidence": 1.0

            })

    df = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Evidence sentences extracted:", len(df))
    print("Saved to:", OUTPUT_FILE)

    return df


if __name__ == "__main__":
    normalize()