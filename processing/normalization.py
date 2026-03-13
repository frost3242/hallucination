import json
import pandas as pd
import os
import re

from config.config import SCRAPED_DATA_FILE, DATA_LAKE_PROCESSED

OUTPUT_FILE = os.path.join(DATA_LAKE_PROCESSED, "knowledge_base/data.csv")


def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text):

    sentences = re.split(r'[.!?]', text)

    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    return sentences


def normalize(json_file=SCRAPED_DATA_FILE):

    print("\nStarting normalization")

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

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