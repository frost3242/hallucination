import pandas as pd

def rank_sources(file):
    """
    Rank data sources based on access type.
    """

    df = pd.read_csv(file)

    score_map = {
        "API": 3,
        "JSON": 2,
        "CSV": 2,
        "OPEN_DATA": 1,
        "WEB": 0
    }

    df["score"] = df["access_type"].map(score_map).fillna(0)

    return df.sort_values("score", ascending=False).reset_index(drop=True)