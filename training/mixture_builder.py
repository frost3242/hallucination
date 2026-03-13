import pandas as pd


def build_dataset(samples, output_file="training_dataset.csv"):
    """
    Builds a clean training dataset by filtering hallucination signals.

    samples: list of dictionaries containing generated data
    output_file: csv file to save dataset
    """

    df = pd.DataFrame(samples)

    # Ensure required columns exist
    required_cols = ["pli", "oci"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Filter low hallucination risk samples
    df = df[df["pli"] < 0.5]
    df = df[df["oci"] == 0]

    # Reset index after filtering
    df = df.reset_index(drop=True)

    # Save dataset
    df.to_csv(output_file, index=False)

    return df