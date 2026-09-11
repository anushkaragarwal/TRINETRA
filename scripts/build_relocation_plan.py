from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PRIORITY_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "habitation_risk_priority.csv"
)

OUTPUT_DIR = ROOT / "data" / "outputs"

RELOCATION_PLAN_PATH = (
    OUTPUT_DIR
    / "relocation_plan.csv"
)

HOST_STATUS_PATH = (
    OUTPUT_DIR
    / "host_capacity_status.csv"
)

UNALLOCATED_GAP_PATH = (
    OUTPUT_DIR
    / "unallocated_relocation_gap.csv"
)


# ---------------------------------------------------------
# EVACUATION-PLANNING ASSUMPTIONS
# ---------------------------------------------------------
# These are planning shares for the MVP, NOT evacuation orders.
# Replace in production using verified vulnerable-person records,
# household-level surveys, DDMA guidance, and official instructions.
# ---------------------------------------------------------
EVACUATION_SHARE = {
    "RED": 0.30,
    "ORANGE": 0.10,
    "YELLOW": 0.00,
    "GREEN": 0.00,
}


# ---------------------------------------------------------
# PROVISIONAL HOST CAPACITY
# ---------------------------------------------------------
# These are placeholders for demonstrating the allocation engine.
# Do NOT claim they are officially verified shelters.
# Production version must use verified DDMA/USDMA/ULB/
# Gram Panchayat shelter-audit data.
# ---------------------------------------------------------
HOST_CLUSTERS = [
    {
        "host_cluster": "Host Cluster A — Safe Zone North",
        "temporary_capacity": 2000,
        "verification_status": (
            "PROVISIONAL — DDMA/USDMA verification required"
        ),
    },
    {
        "host_cluster": "Host Cluster B — Safe Zone Central",
        "temporary_capacity": 2500,
        "verification_status": (
            "PROVISIONAL — DDMA/USDMA verification required"
        ),
    },
    {
        "host_cluster": "Host Cluster C — Safe Zone South",
        "temporary_capacity": 2000,
        "verification_status": (
            "PROVISIONAL — DDMA/USDMA verification required"
        ),
    },
    {
        "host_cluster": "Host Cluster D — Reserve Capacity",
        "temporary_capacity": 1500,
        "verification_status": (
            "PROVISIONAL — DDMA/USDMA verification required"
        ),
    },
]


def get_relocation_action(zone):
    actions = {
        "RED": (
            "Prioritize vulnerable households; "
            "prepare transport and temporary shelter allocation"
        ),
        "ORANGE": (
            "Keep vulnerable residents on standby; "
            "reserve capacity and issue pre-alert"
        ),
        "YELLOW": (
            "Monitor only; no relocation allocation at this stage"
        ),
        "GREEN": (
            "Routine monitoring; no relocation allocation"
        ),
    }
    return actions.get(zone, "Manual review required")


def allocate_people(demand_df, host_df):
    """
    Allocate planned relocation demand to host capacity.

    Allocation order:
    1. Highest habitation priority score first.
    2. Red Zones are automatically above Orange Zones because
       they generally have higher priority scores.
    3. Host Cluster A -> B -> C -> D.
    """

    available_capacity = (
        host_df["temporary_capacity"]
        .tolist()
    )

    allocation_rows = []
    unallocated_rows = []

    sorted_demand = demand_df.sort_values(
        by=[
            "red_zone_label",
            "habitation_priority_score",
        ],
        ascending=[
            True,
            False,
        ],
    ).copy()

    # Explicit zone priority avoids depending on alphabetical order.
    zone_priority = {
        "RED": 1,
        "ORANGE": 2,
        "YELLOW": 3,
        "GREEN": 4,
    }

    sorted_demand["zone_priority"] = (
        sorted_demand["red_zone_label"]
        .map(zone_priority)
    )

    sorted_demand = sorted_demand.sort_values(
        by=[
            "zone_priority",
            "habitation_priority_score",
        ],
        ascending=[
            True,
            False,
        ],
    )

    for _, row in sorted_demand.iterrows():
        remaining_people = int(
            row["people_to_relocate"]
        )

        if remaining_people <= 0:
            continue

        original_people = remaining_people

        for host_index, host in host_df.iterrows():
            if remaining_people <= 0:
                break

            available = available_capacity[host_index]

            if available <= 0:
                continue

            allocated = min(
                remaining_people,
                available,
            )

            available_capacity[host_index] -= allocated
            remaining_people -= allocated

            allocation_rows.append({
                "source_habitation": row["NAME"],
                "source_zone": row["red_zone_label"],
                "source_priority_score": (
                    row["habitation_priority_score"]
                ),
                "source_population_2026_est": (
                    row["POP_2026_EST"]
                ),
                "planned_evacuation_share": (
                    row["planned_evacuation_share"]
                ),
                "people_to_relocate": original_people,
                "host_cluster": host["host_cluster"],
                "allocated_people": allocated,
                "host_verification_status": (
                    host["verification_status"]
                ),
                "allocation_status": "ALLOCATED",
                "recommended_action": (
                    row["relocation_action"]
                ),
            })

        if remaining_people > 0:
            unallocated_rows.append({
                "source_habitation": row["NAME"],
                "source_zone": row["red_zone_label"],
                "source_priority_score": (
                    row["habitation_priority_score"]
                ),
                "source_population_2026_est": (
                    row["POP_2026_EST"]
                ),
                "people_to_relocate": original_people,
                "unallocated_people": remaining_people,
                "gap_action": (
                    "Activate additional verified shelters; "
                    "request inter-area support; "
                    "arrange phased/priority evacuation"
                ),
            })

    host_df = host_df.copy()
    host_df["allocated_people"] = [
        capacity - remaining
        for capacity, remaining in zip(
            host_df["temporary_capacity"],
            available_capacity,
        )
    ]

    host_df["remaining_capacity"] = available_capacity

    host_df["capacity_utilisation_pct"] = (
        host_df["allocated_people"]
        / host_df["temporary_capacity"]
        * 100
    ).round(2)

    return allocation_rows, unallocated_rows, host_df


def main():
    print("📥 Loading habitation priority table...")

    priority = pd.read_csv(PRIORITY_PATH)

    # Add a transparent planned evacuation share by zone.
    priority["planned_evacuation_share"] = (
        priority["red_zone_label"]
        .map(EVACUATION_SHARE)
        .fillna(0)
    )

    # Estimated temporary-relocation planning load.
    priority["people_to_relocate"] = (
        priority["POP_2026_EST"]
        * priority["planned_evacuation_share"]
    ).round().astype(int)

    priority["relocation_action"] = (
        priority["red_zone_label"]
        .apply(get_relocation_action)
    )

    demand = priority[
        priority["people_to_relocate"] > 0
    ].copy()

    print("\n📌 Planned relocation demand by zone:")
    print(
        demand.groupby("red_zone_label")[
            "people_to_relocate"
        ]
        .sum()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\n📌 Total planned relocation demand:")
    print(
        int(
            demand["people_to_relocate"]
            .sum()
        )
    )

    host_capacity = pd.DataFrame(HOST_CLUSTERS)

    print("\n🏠 Provisional total host capacity:")
    print(
        int(
            host_capacity["temporary_capacity"]
            .sum()
        )
    )

    allocation_rows, unallocated_rows, host_status = (
        allocate_people(
            demand,
            host_capacity,
        )
    )

    relocation_plan = pd.DataFrame(allocation_rows)

    if unallocated_rows:
        unallocated_gap = pd.DataFrame(unallocated_rows)
    else:
        unallocated_gap = pd.DataFrame(
            columns=[
                "source_habitation",
                "source_zone",
                "source_priority_score",
                "source_population_2026_est",
                "people_to_relocate",
                "unallocated_people",
                "gap_action",
            ]
        )

    total_demand = int(
        demand["people_to_relocate"]
        .sum()
    )

    total_allocated = int(
        relocation_plan["allocated_people"]
        .sum()
    ) if not relocation_plan.empty else 0

    total_unallocated = int(
        unallocated_gap["unallocated_people"]
        .sum()
    ) if not unallocated_gap.empty else 0

    print("\n📊 Allocation summary:")
    print(f"People requiring planned relocation: {total_demand}")
    print(f"People allocated to host clusters: {total_allocated}")
    print(f"Unallocated capacity gap: {total_unallocated}")

    print("\n🏠 Host capacity status:")
    print(
        host_status.to_string(
            index=False
        )
    )

    if not relocation_plan.empty:
        print("\n🚍 Relocation allocation plan:")
        print(
            relocation_plan.to_string(
                index=False
            )
        )

    if not unallocated_gap.empty:
        print("\n⚠️ Unallocated relocation gap:")
        print(
            unallocated_gap.to_string(
                index=False
            )
        )
    else:
        print("\n✅ No capacity gap detected.")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    relocation_plan.to_csv(
        RELOCATION_PLAN_PATH,
        index=False,
    )

    host_status.to_csv(
        HOST_STATUS_PATH,
        index=False,
    )

    unallocated_gap.to_csv(
        UNALLOCATED_GAP_PATH,
        index=False,
    )

    print(
        f"\n✅ Saved relocation plan:\n"
        f"{RELOCATION_PLAN_PATH}"
    )

    print(
        f"✅ Saved host capacity status:\n"
        f"{HOST_STATUS_PATH}"
    )

    print(
        f"✅ Saved unallocated gap report:\n"
        f"{UNALLOCATED_GAP_PATH}"
    )


if __name__ == "__main__":
    main()