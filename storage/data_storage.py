import os
import json
import pandas as pd

DATA_LAKE_RAW = "data_lake/raw/"
DATA_LAKE_PROCESSED = "data_lake/processed/"


def save_raw_json(data, name):
    """
    Save raw JSON data to raw data lake.
    """

    os.makedirs(DATA_LAKE_RAW, exist_ok=True)

    path = os.path.join(DATA_LAKE_RAW, f"{name}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return path


def save_processed_csv(df, name):
    """
    Save processed dataframe to processed data lake.
    """

    os.makedirs(DATA_LAKE_PROCESSED, exist_ok=True)

    path = os.path.join(DATA_LAKE_PROCESSED, f"{name}.csv")

    df.to_csv(path, index=False)

    return path