from pathlib import Path
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)

SENTINEL1_IMAGE_PATH = (
    ROOT
    / "assets"
    / "satellite"
    / "sentinel1_sar_analysis.png"
)

SENTINEL2_IMAGE_PATH = (
    ROOT
    / "assets"
    / "satellite"
    / "sentinel2_optical_analysis.png"
)


st.set_page_config(
    page_title="TRINETRA | River Hazard Dashboard",
    page_icon="🌊",
    layout="wide",
)


def risk_color(level):
    level = str(level).upper()

    if level == "CRITICAL":
        return "#DC2626"

    if level == "HIGH":
        return "#EA580C"

    if level == "MODERATE":
        return "#CA8A04"

    return "#16A34A"


def evidence_color(evidence_class):
    evidence_class = str(evidence_class).upper()

    if "STRONG" in evidence_class:
        return "#DC2626"

    if "MODERATE" in evidence_class:
        return "#EA580C"

    if "WEAK" in evidence_class:
        return "#CA8A04"

    return "#64748B"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def main():
    st.title("🌊 TRINETRA")

    st.caption(
        "Explainable river-hazard assessment using hydrological "
        "signals and independent satellite evidence."
    )

    if not DATA_PATH.exists():
        st.error(
            "Dashboard data file was not found. Run "
            "`python scripts/build_final_trinetra_event_output.py` "
            "first."
        )
        st.stop()

    df = load_data()

    if df.empty:
        st.error("The dashboard data file is empty.")
        st.stop()

    event = df.iloc[0]

    hydrological_score = float(
        event["hydrological_risk_score_0_100"]
    )

    satellite_score = float(
        event["satellite_evidence_score_0_100"]
    )

    hydrological_level = str(
        event["hydrological_risk_level"]
    )

    satellite_class = str(
        event["satellite_evidence_class"]
    )

    satellite_status = str(
        event["satellite_evidence_status"]
    )

    st.divider()

    st.subheader("Selected Event")

    left, right = st.columns(2)

    with left:
        st.write(
            f"**Station:** {event['station_name']}"
        )

        st.write(
            f"**Event time (IST):** {event['event_time_ist']}"
        )

        st.write(
            f"**Coordinates:** "
            f"{float(event['latitude']):.6f}° N, "
            f"{float(event['longitude']):.4f}° E"
        )

    with right:
        st.write(
            f"**Event ID:** `{event['event_id']}`"
        )

        st.write(
            "**Analysis area:** 10 km radius around "
            "the river station"
        )

    st.divider()

    st.subheader("Risk and Satellite Evidence")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Hydrological Risk Score",
            value=f"{hydrological_score:.0f} / 100",
            help=(
                "Score generated from the TRINETRA "
                "river-hydrology hazard pipeline."
            ),
            border=True,
        )

        st.markdown(
            f"""
            <div style="
                background-color: {risk_color(hydrological_level)};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 8px;
            ">
                {hydrological_level}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric(
            label="Satellite Evidence Score",
            value=f"{satellite_score:.2f} / 100",
            help=(
                "A conservative score representing "
                "satellite-observed post-event water-change evidence."
            ),
            border=True,
        )

        st.markdown(
            f"""
            <div style="
                background-color: {evidence_color(satellite_class)};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 8px;
            ">
                INCONCLUSIVE
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.metric(
            label="System Recommendation",
            value="Monitor urgently",
            help=(
                "Critical river risk requires monitoring even "
                "when satellite flood evidence is inconclusive."
            ),
            border=True,
        )

        st.info(
            "Do not interpret a high hydrological risk score "
            "as automatic satellite-confirmed flooding."
        )

    st.divider()

    st.subheader("System Interpretation")

    st.warning(
        "⚠️ **Critical hydrological risk detected.** "
        "Satellite analysis is inconclusive for widespread "
        "post-event inundation within the selected 10 km AOI. "
        "Continue monitoring and verify conditions using official "
        "reports and local observations."
    )

    st.write(
        event["system_interpretation"]
    )

    st.divider()

    st.subheader("Satellite Analysis Details")

    s2_col, s1_col = st.columns(2)

    with s2_col:
        st.markdown("### Sentinel-2 Optical Evidence")

        st.metric(
            "Candidate New Water",
            f"{float(event['sentinel2_candidate_new_water_ha']):.2f} ha",
            border=True,
        )

        st.metric(
            "Net Water-Area Change",
            f"{float(event['sentinel2_net_water_change_ha']):.2f} ha",
            border=True,
        )

        st.caption(
            "Sentinel-2 uses cloud-masked optical imagery and "
            "MNDWI-based candidate water mapping."
        )

    with s1_col:
        st.markdown("### Sentinel-1 SAR Evidence")

        st.metric(
            "Mean VV Backscatter Change",
            f"{float(event['sentinel1_mean_vv_change_db']):+.2f} dB",
            border=True,
        )

        st.metric(
            "Candidate New SAR Water",
            f"{float(event['sentinel1_candidate_new_water_ha']):.4f} ha",
            border=True,
        )

        st.caption(
            "Sentinel-1 SAR uses ascending-orbit VV "
            "before/after comparison and is less affected by clouds."
        )

    st.divider()

    st.subheader("Satellite Evidence Maps")

    st.caption(
        "Exploratory satellite-derived layers for the selected "
        "10 km AOI. These are analysis outputs and do not "
        "independently confirm flood extent."
    )

    image_col1, image_col2 = st.columns(2)

    with image_col1:
        st.markdown("### Sentinel-1 SAR Analysis")

        if SENTINEL1_IMAGE_PATH.exists():
            st.image(
                str(SENTINEL1_IMAGE_PATH),
                caption=(
                    "Sentinel-1 SAR VV backscatter / candidate "
                    "water-change analysis (ascending orbit)."
                ),
                use_container_width=True,
            )
        else:
            st.info(
                "Image not found. Add this file: "
                "`assets/satellite/sentinel1_sar_analysis.png`"
            )

    with image_col2:
        st.markdown("### Sentinel-2 Optical Analysis")

        if SENTINEL2_IMAGE_PATH.exists():
            st.image(
                str(SENTINEL2_IMAGE_PATH),
                caption=(
                    "Sentinel-2 cloud-masked MNDWI / candidate "
                    "water-change analysis."
                ),
                use_container_width=True,
            )
        else:
            st.info(
                "Image not found. Add this file: "
                "`assets/satellite/sentinel2_optical_analysis.png`"
            )

    st.divider()

    st.subheader("Evidence Summary")

    summary_table = pd.DataFrame(
        {
            "Data source": [
                "River hydrology model",
                "Sentinel-2 optical imagery",
                "Sentinel-1 SAR imagery",
            ],
            "Key result": [
                (
                    f"{hydrological_score:.0f}/100 — "
                    f"{hydrological_level}"
                ),
                (
                    f"New water: "
                    f"{float(event['sentinel2_candidate_new_water_ha']):.2f} ha; "
                    f"net change: "
                    f"{float(event['sentinel2_net_water_change_ha']):.2f} ha"
                ),
                (
                    f"VV change: "
                    f"{float(event['sentinel1_mean_vv_change_db']):+.2f} dB; "
                    f"candidate water: "
                    f"{float(event['sentinel1_candidate_new_water_ha']):.4f} ha"
                ),
            ],
            "Interpretation": [
                "Critical river-risk condition.",
                "No net optical water expansion in the selected AOI.",
                "No strong SAR evidence of widespread new open water.",
            ],
        }
    )

    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    with st.expander("View complete dashboard data"):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        f"Satellite evidence status: {satellite_status}. "
        "This dashboard is an academic prototype and not an "
        "official emergency-alert system."
    )


if __name__ == "__main__":
    main()