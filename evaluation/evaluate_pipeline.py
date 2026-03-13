import json
import os
import sys

# Ensure base directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hallucination.oci_detector import detect_oci
from hallucination.pli_detector import detect_pli
from hallucination.semantic_detector import semantic_relevance
from config.config import OCI_WEIGHT, PLI_WEIGHT, RELEVANCE_WEIGHT, HIGH_RISK_THRESHOLD

def calculate_final_risk(oci_result, pli_result, semantic_result):
    """
    Computes a single risk score based on the weights in config.py
    """
    oci_risk = oci_result["hallucination_risk_score"]
    pli_risk = pli_result["pli_score"]
    sem_risk = semantic_result["relevance_risk"]
    
    total_risk = (oci_risk * OCI_WEIGHT) + (pli_risk * PLI_WEIGHT) + (sem_risk * RELEVANCE_WEIGHT)
    return total_risk

def evaluate_current_system():
    """
    Evaluates the current configuration against a golden validation set.
    Returns: A float representing accuracy/score (0.0 to 1.0) where 1.0 is perfect classification.
    """
    # Hardcoded mini validation set for fast autoresearch loop
    golden_data = [
        {
            "premise": "Aspirin is indicated for the relief of minor aches and pains and to reduce fever.",
            "tests": [
                {"hypothesis": "Aspirin can help reduce fever and relieve minor pain.", "label": 0}, # True statement
                {"hypothesis": "Aspirin is primarily used to increase body temperature and cause fever.", "label": 1}, # Contradiction
                {"hypothesis": "Aspirin might occasionally be used to treat bacterial infections.", "label": 1} # Unsupported/Hallucination
            ]
        },
        {
            "premise": "Lisinopril is an ACE inhibitor used to treat high blood pressure and heart failure.",
            "tests": [
                {"hypothesis": "Lisinopril is used for managing high blood pressure.", "label": 0},
                {"hypothesis": "Lisinopril is an antibiotic used to cure viral infections.", "label": 1}
            ]
        }
    ]

    correct_predictions = 0
    total_predictions = 0

    for item in golden_data:
        premise = item["premise"]
        for test in item["tests"]:
            hypothesis = test["hypothesis"]
            true_label = test["label"]

            # Run through the un-modified base detectors
            oci_res = detect_oci(premise, hypothesis)
            pli_res = detect_pli(premise, hypothesis)
            sem_res = semantic_relevance(premise, hypothesis)

            # Combine using weights from config.py
            final_risk = calculate_final_risk(oci_res, pli_res, sem_res)
            
            # Predict hallucination (1) if risk > threshold, else 0
            predicted_label = 1 if final_risk >= HIGH_RISK_THRESHOLD else 0

            if predicted_label == true_label:
                correct_predictions += 1
            
            total_predictions += 1

    score = correct_predictions / total_predictions if total_predictions > 0 else 0.0
    return score

if __name__ == "__main__":
    score = evaluate_current_system()
    print(f"Current System Evaluation Score: {score:.4f}")
