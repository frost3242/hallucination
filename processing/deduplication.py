def deduplicate_sources(df):
    """
    Removes exact duplicate evidence sentences from the dataset.
    """
    if df.empty or "evidence_sentence" not in df.columns:
        return df

    # Drop duplicate exact sentences, keeping the first occurrence
    df = df.drop_duplicates(subset=["evidence_sentence"])

    return df.reset_index(drop=True)