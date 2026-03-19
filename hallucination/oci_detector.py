from transformers import pipeline

# Load NLI model once
nli_model = pipeline(
    "text-classification",
    model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
)


def detect_oci(premise, hypothesis):
    """
    Object/Claim Inconsistency (OCI) detector.

    premise: factual context
    hypothesis: generated statement

    Returns hallucination risk score and OCI flag.
    """

    # Step 1: NLI evaluation
    result = nli_model(f"{premise} </s></s> {hypothesis}")

    label = result[0]["label"].upper()
    score = result[0]["score"]

    # Step 2: Contradiction probability
    if label == "CONTRADICTION":
        contradiction_prob = score

    elif label == "NEUTRAL":
        # Strict Extraction Mode: Unsupported facts are full hallucinations
        contradiction_prob = 1.0

    else:  # ENTAILMENT
        contradiction_prob = 0.0

    # Step 3: Confidence bias approximation
    confidence_bias = contradiction_prob + (1 - contradiction_prob) * 0.2

    # Step 4: OCI hallucination risk score
    hallucination_risk_score = (
        0.6 * contradiction_prob +
        0.4 * confidence_bias
    )

    # Step 5: OCI decision flag
    oci_flag = 1 if hallucination_risk_score > 0.6 else 0

    return {
        "nli_label": label,
        "contradiction_probability": round(contradiction_prob, 3),
        "hallucination_risk_score": round(hallucination_risk_score, 3),
        "oci_flag": oci_flag
    }