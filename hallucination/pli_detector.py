from transformers import pipeline

# Load the NLI model once when the module is imported
nli_model = pipeline(
    "text-classification",
    model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
)


def detect_pli(premise, hypothesis):
    """
    Premise–Hypothesis Logical Inconsistency detector.

    premise: factual context (drug indication text)
    hypothesis: generated statement

    Returns:
        pli_label
        pli_score (hallucination risk)
    """

    result = nli_model(f"{premise} </s></s> {hypothesis}")

    label = result[0]["label"].upper()
    score = result[0]["score"]

    # Convert NLI output to hallucination risk score
    if label == "CONTRADICTION":
        pli_score = score

    elif label == "NEUTRAL":
        pli_score = score * 0.5

    else:  # ENTAILMENT
        pli_score = 0.0

    return {
        "pli_label": label,
        "pli_score": round(pli_score, 3)
    }