import pandas as pd
import os
from discovery.dataset_classifier import classify_source


def build_registry(df):
    """
    Build a metadata registry for discovered data sources.
    """

    rows = []

    for _, r in df.iterrows():

        url = r.get("url")
        domain = r.get("domain", "unknown")

        rows.append({
            "source_id": url,
            "access_type": classify_source(url),
            "license": "unknown",
            "update_frequency": "unknown",
            "format": "unknown",
            "domain_coverage": domain,
            "overlap_risk": "unknown"
        })

    registry = pd.DataFrame(rows)

    # Ensure metadata folder exists
    os.makedirs("metadata", exist_ok=True)

    registry.to_csv("metadata/source_registry.csv", index=False)

    return registry.reset_index(drop=True)