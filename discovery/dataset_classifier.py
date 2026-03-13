def classify_source(url):

    url = url.lower()

    # File formats first
    if ".json" in url:
        return "JSON"

    if ".csv" in url:
        return "CSV"

    # API endpoints
    if "api" in url:
        return "API"

    # Open data portals
    if "data" in url or "dataset" in url:
        return "OPEN_DATA"

    # Default
    return "WEB"