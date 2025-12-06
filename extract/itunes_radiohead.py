from pathlib import Path

import pandas as pd
import requests

# Base directory of the project (dw_radiohead)
BASE_DIR = Path(__file__).resolve().parent.parent

# Output path for the API snapshot
OUTPUT_PATH = BASE_DIR / "data" / "itunes_radiohead_raw.csv"


def main():
    """
    Extraction step that connects directly to a public API via Python.

    We call the iTunes Search API to fetch a small snapshot of Radiohead songs.
    This satisfies the project requirement:
    - "Use Fivetran OR connect directly to an API via Python".

    API docs (legacy, but still valid):
    https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTunesWebServicesSearchAPI/
    """
    print("[API EXTRACT] Calling iTunes Search API for Radiohead tracks...")

    url = "https://itunes.apple.com/search"
    params = {
        "term": "radiohead",
        "entity": "song",
        "limit": 50,  # keep it small and simple
    }

    # Send HTTP GET request
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    # Parse JSON
    data = response.json().get("results", [])
    print(f"[API EXTRACT] Received {len(data)} records from iTunes API.")

    if not data:
        raise RuntimeError(
            "iTunes API returned no results. "
            "Please check the API endpoint or parameters."
        )

    # Normalize JSON into a flat pandas DataFrame
    df = pd.json_normalize(data)

    # Keep only a few useful fields to make the table lighter
    columns_to_keep = [
        "trackName",
        "artistName",
        "collectionName",
        "primaryGenreName",
        "trackTimeMillis",
        "releaseDate",
    ]
    df = df[columns_to_keep]

    # Save snapshot CSV for Snowflake loading
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"[API EXTRACT] Saving API snapshot to: {OUTPUT_PATH}")
    df.to_csv(OUTPUT_PATH, index=False)

    print("[API EXTRACT] iTunes API extraction completed successfully.")


if __name__ == "__main__":
    main()
