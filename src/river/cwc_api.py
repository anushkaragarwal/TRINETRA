
import json
import requests
import pandas as pd

from config import (
    CWC_API_URL,
    CWC_RESOURCE_ID,
    CWC_API_TIMEOUT,
    CWC_BATCH_SIZE,
    CWC_STATE,
    CWC_DISTRICT,
    CWC_AGENCY,
)


def fetch_cwc_batch(
    offset=0,
    limit=CWC_BATCH_SIZE,
):
    """
    Fetch one batch of CWC records from the NWDP API.
    """

    # NWDP expects filters as a JSON-encoded string
    filters = json.dumps({
        "State": CWC_STATE,
        "District": CWC_DISTRICT,
        "Agency": CWC_AGENCY,
    })

    params = {
        "resource_id": CWC_RESOURCE_ID,
        "filters": filters,
        "limit": limit,
        "offset": offset,
    }

    print(
        f"🌐 Fetching CWC API batch "
        f"(offset={offset}, limit={limit})..."
    )

    response = requests.get(
        CWC_API_URL,
        params=params,
        timeout=CWC_API_TIMEOUT,
    )

    print(f"   HTTP status: {response.status_code}")

    response.raise_for_status()

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(
            f"CWC API returned an unsuccessful response: {data}"
        )

    result = data.get("result", {})

    records = result.get("records", [])
    total = result.get("total", 0)

    print(
        f"   Received {len(records)} records "
        f"(total available: {total})"
    )

    return records, total


def fetch_all_cwc_data(
    batch_size=CWC_BATCH_SIZE,
):
    """
    Fetch all available CWC records in batches.
    """

    all_records = []
    offset = 0

    while True:

        records, total = fetch_cwc_batch(
            offset=offset,
            limit=batch_size,
        )

        if not records:
            break

        all_records.extend(records)

        offset += len(records)

        print(
            f"📊 Progress: "
            f"{len(all_records)} / {total}"
        )

        if offset >= total:
            break

    print("\n✅ Finished API download.")

    print(
        f"📊 Total records downloaded: "
        f"{len(all_records)}"
    )

    return pd.DataFrame(all_records)


def fetch_cwc_data():
    """
    Main CWC API function.
    """

    df = fetch_all_cwc_data()

    if df.empty:
        raise RuntimeError(
            "CWC API returned no records."
        )

    return df