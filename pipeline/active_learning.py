def select_hard_cases(df):
    """
    Selects difficult samples for active learning.
    """

    hard_cases = df[
        (df["pli"] > 0.5) |   # higher contradiction risk
        (df["oci"] == 1)      # hallucination detected
    ]

    return hard_cases.reset_index(drop=True)