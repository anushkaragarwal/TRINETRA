# TRINETRA - IMD / NWDP Rainfall API

import json

import pandas as pd
import requests

from config import (
    RAINFALL_API_URL,
    RAINFALL_RESOURCE_ID,
    RAINFALL_API_TIMEOUT,
    RAINFALL_BATCH_SIZE,
    RAINFALL_STATE,
    RAINFALL_DISTRICT,
)


def fetch_rainfall_batch(
    offset=0,
    limit=RAINFALL_BATCH_SIZE,
):
    """
    Fetch one batch of district-wise rainfall
    data from NWDP / IMD.
    """

    filters = json.dumps({
        "State": RAINFALL_STATE,
        "District": RAINFALL_DISTRICT,
    })

    params = {
        "resource_id": RAINFALL_RESOURCE_ID,
        "filters": filters,
        "limit": limit,
        "offset": offset,
    }

    print(
        f"🌧️ Fetching rainfall API batch "
        f"(offset={offset}, limit={limit})..."
    )

    response = requests.get(
        RAINFALL_API_URL,
        params=params,
        timeout=RAINFALL_API_TIMEOUT,
    )

    print(
        f"   HTTP status: {response.status_code}"
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(
            "Rainfall API returned an unsuccessful response."
        )

    result = data.get("result", {})

    records = result.get(
        "records",
        [],
    )

    total = result.get(
        "total",
        0,
    )

    print(
        f"   Received {len(records)} records "
        f"(total available: {total})"
    )

    return records, total


def fetch_all_rainfall_data(
    batch_size=RAINFALL_BATCH_SIZE,
):
    """
    Fetch all available Chamoli rainfall records.
    """

    all_records = []

    offset = 0

    while True:

        records, total = fetch_rainfall_batch(
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

    print(
        "\n✅ Finished rainfall API download."
    )

    print(
        f"📊 Total rainfall records: "
        f"{len(all_records)}"
    )

    return pd.DataFrame(
        all_records
    )


def fetch_rainfall_data():

    df = fetch_all_rainfall_data()

    if df.empty:
        raise RuntimeError(
            "Rainfall API returned no records."
        )

    return df