import sys, json, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config import HIGH_RISK_THRESHOLD, OCI_WEIGHT, PLI_WEIGHT, RELEVANCE_WEIGHT
print("Imports starting...")
from hallucination.oci_detector import detect_oci
from hallucination.pli_detector import detect_pli
from hallucination.semantic_detector import semantic_relevance
print("Imports finished.")

with open('evaluation/golden_data.json', 'r') as f:
    data = json.load(f)

for item in data:
    for test in item['tests']:
        p = item['premise']
        h = test['hypothesis']
        print(f"\n--- EVALUATING: {h[:30]}...")
        oci = detect_oci(p, h)['hallucination_risk_score']
        pli = detect_pli(p, h)['pli_score']
        sem = semantic_relevance(p, h)['relevance_risk']
        
        total_risk = (oci * OCI_WEIGHT) + (pli * PLI_WEIGHT) + (sem * RELEVANCE_WEIGHT)
        
        print(f"OCI={oci}, PLI={pli}, SEM={sem:.2f} | TOTAL RISK = {total_risk:.3f}")
        print(f"TRUE LABEL: {test['label']} | PREDICTED: {1 if total_risk >= HIGH_RISK_THRESHOLD else 0}")
print("Done.")
