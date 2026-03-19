import os, sys, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hallucination.oci_detector import detect_oci
from hallucination.pli_detector import detect_pli
from hallucination.semantic_detector import semantic_relevance

def debug():
    with open('evaluation/golden_data.json', 'r') as f:
        data = json.load(f)

    results = []
    for i, item in enumerate(data):
        for j, test in enumerate(item['tests']):
            p = item['premise']
            h = test['hypothesis']
            true_label = test['label']
            oci = detect_oci(p, h)['hallucination_risk_score']
            pli = detect_pli(p, h)['pli_score']
            sem = semantic_relevance(p, h)['relevance_risk']
            results.append(f"Q{i}-{j} (Label {true_label}): OCI={oci}, PLI={pli}, SEM={sem:.2f} | Hyp: {h}")

    with open('evaluation_debug.txt', 'w') as f:
        f.write("\n".join(results))

if __name__ == '__main__':
    debug()
