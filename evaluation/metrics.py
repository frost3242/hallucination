import numpy as np


def pli_rate(scores):
    """
    Average PLI contradiction score.
    """
    scores = np.array(scores)

    if scores.size == 0:
        return 0.0

    return float(np.mean(scores))


def oci_rate(flags):
    """
    Fraction of samples flagged as hallucination by OCI.
    """
    flags = np.array(flags)

    if flags.size == 0:
        return 0.0

    return float(np.mean(flags))


def semantic_risk_rate(risks):
    """
    Average semantic hallucination risk.
    """
    risks = np.array(risks)

    if risks.size == 0:
        return 0.0

    return float(np.mean(risks))