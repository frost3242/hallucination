def deduplicate_sources(df):

    df["url"] = df["url"].str.rstrip("/")

    df = df.drop_duplicates(subset=["url"])

    return df.reset_index(drop=True)