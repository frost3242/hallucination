from ddgs import DDGS
import pandas as pd


def find_apis(domain, max_results=20):
    """
    Search the web for APIs, datasets, and registries related to a domain.
    """

    queries = [
        f"{domain} API",
        f"{domain} dataset json",
        f"{domain} open data",
        f"{domain} public API",
        f"{domain} registry database"
    ]

    sources = []
    seen_urls = set()

    with DDGS() as ddgs:

        for q in queries:

            results = ddgs.text(q, max_results=max_results)

            for r in results:

                title = r.get("title")
                url = r.get("href")

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                sources.append({
                    "title": title,
                    "url": url,
                    "domain": domain
                })

    df = pd.DataFrame(sources)

    return df.reset_index(drop=True)