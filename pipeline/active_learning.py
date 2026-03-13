import json
import os
import random
import pandas as pd
import re
import sys

# Ensure base directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synthetic.generator import generate

def select_hard_cases(df):
    """
    Selects difficult samples for active learning.
    """
    if "pli" in df.columns and "oci" in df.columns:
        hard_cases = df[
            (df["pli"] > 0.5) |   # higher contradiction risk
            (df["oci"] == 1)      # hallucination detected
        ]
        return hard_cases.reset_index(drop=True)
    return df

def generate_active_learning_samples(csv_file, samples=1):
    """
    Reads a processed CSV, picks random sentences, generates synthetic
    tests, and appends them to golden_data.json.
    """
    df = pd.read_csv(csv_file)
    if df.empty or "evidence_sentence" not in df.columns:
        return
    
    sentences = df["evidence_sentence"].dropna().unique().tolist()
    if not sentences:
        return
        
    sampled_sents = random.sample(sentences, min(samples, len(sentences)))
    
    golden_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation", "golden_data.json")
    
    try:
        with open(golden_path, "r", encoding="utf-8") as f:
            golden_data = json.load(f)
    except FileNotFoundError:
        golden_data = []
        
    new_additions = 0
    for text in sampled_sents:
        try:
            print(f"   Drafting synthetic tests for: {text[:50]}...")
            res = generate(text)
            
            # Extract JSON from potential markdown blocks
            match = re.search(r"\{.*\}", res, re.DOTALL)
            if match:
                res_dict = json.loads(match.group(0))
                
                new_entry = {
                    "premise": text,
                    "tests": [
                        {"hypothesis": res_dict.get("true_statement", ""), "label": 0},
                        {"hypothesis": res_dict.get("contradiction_statement", ""), "label": 1},
                        {"hypothesis": res_dict.get("uncertain_statement", ""), "label": 1}
                    ]
                }
                golden_data.append(new_entry)
                new_additions += 1
        except Exception as e:
            print(f"Failed to generate for a sentence: {e}")
            
    if new_additions > 0:
        with open(golden_path, "w", encoding="utf-8") as f:
            json.dump(golden_data, f, indent=2)
        print(f"   Saved {new_additions} new test cases to golden_data.json")