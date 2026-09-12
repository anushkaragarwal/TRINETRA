import requests

BACKEND_URL = "http://127.0.0.1:8000"
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


# ------------------------------------------------------------
# Rainfall dashboard data
# ------------------------------------------------------------

RAINFALL_HAZARD_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_hybrid_hazard.csv"
)

RAINFALL_FORECAST_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_forecast_predictions.csv"
)

RAINFALL_DAILY_RISK_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk_daily.csv"
)


st.set_page_config(
    page_title="TRINETRA | River + Rainfall Hazard Dashboard",
    page_icon="🌊🌧️",
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


@st.cache_data
def load_rainfall_hazard():

    return pd.read_csv(
        RAINFALL_HAZARD_PATH,
        parse_dates=["Date"],
    )


@st.cache_data
def load_rainfall_forecast():

    return pd.read_csv(
        RAINFALL_FORECAST_PATH,
        parse_dates=["Date"],
    )


@st.cache_data
def load_rainfall_daily_risk():

    return pd.read_csv(
        RAINFALL_DAILY_RISK_PATH,
        parse_dates=["date"],
    )


def main():

    st.title("🌊🌧️ TRINETRA")

    st.caption(
        "Integrated river, rainfall, and terrain hazard assessment "
        "using hydrological signals, DEM-derived terrain intelligence, "
        "rainfall intelligence, and independent satellite evidence."
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

        st.error(
            "The dashboard data file is empty."
        )

        st.stop()

    event = df.iloc[0]

    hydrological_score = float(
        event["hydrological_risk_score_0_100"]
    )

    terrain_score = float(
        event["terrain_hazard_score_0_100"]
    )

    trinetra_score = float(
        event["trinetra_hazard_score_0_100"]
    )

    trinetra_level = str(
        event["trinetra_hazard_level"]
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

    st.subheader("🌊 Selected River Event")


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

    st.subheader(
        "Risk and Satellite Evidence"
    )


    col1, col2, col3, col4 = st.columns(4)

    # ---------------------------------------------------------
    # TRINETRA COMBINED HAZARD
    # ---------------------------------------------------------

    with col1:
        st.metric(
            label="TRINETRA Hazard Score",
            value=f"{trinetra_score:.0f} / 100",
            help=(
                "Combined MVP hazard index based on "
                "hydrological risk and local DEM-derived "
                "terrain hazard."
            ),
            border=True,
        )

        st.markdown(
            f"""
            <div style="
                background-color: {risk_color(trinetra_level)};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 8px;
            ">
                {trinetra_level}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # HYDROLOGICAL RISK
    # ---------------------------------------------------------

    with col2:
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

    # ---------------------------------------------------------
    # SATELLITE EVIDENCE
    # ---------------------------------------------------------

    with col3:
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
                {satellite_class}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ============================================================
# HAZARD ZONE MAP
# ============================================================

st.divider()
st.subheader("🗺️ TRINETRA Hazard Zones")

try:
    hazard_response = requests.get(
        f"{BACKEND_URL}/api/hazard-zones",
        timeout=30
    )
    hazard_response.raise_for_status()

    hazard_data = hazard_response.json()
    zones = hazard_data.get("zones", [])

    if zones:

        hazard_df = pd.DataFrame(zones)

        # Map data
        map_df = hazard_df[
            ["lat", "lon", "hazard_score", "risk_level", "type"]
        ].copy()

        map_df["size"] = map_df["hazard_score"]

        st.map(
            map_df,
            latitude="lat",
            longitude="lon",
            size="size",
            zoom=9,
        )

        st.caption(
            "Hazard locations are derived from the current "
            "TRINETRA multi-hazard assessment."
        )

        st.dataframe(
            hazard_df[
                ["type", "hazard_score", "risk_level", "lat", "lon"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.warning("No hazard-zone data available.")

except Exception as e:
    st.error(f"Unable to load hazard zones: {e}")    

    # ---------------------------------------------------------
    # DEM TERRAIN HAZARD
    # ---------------------------------------------------------

    with col4:
        terrain_level = str(
            event["terrain_hazard_level"]
        )

        st.metric(
            label="Terrain Hazard Score",
            value=f"{terrain_score:.0f} / 100",
            help=(
                "Local DEM-derived terrain hazard score "
                "calculated around the event."
            ),
            border=True,
        )

        st.markdown(
            f"""
            <div style="
                background-color: {risk_color(terrain_level)};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 8px;
            ">
                {terrain_level}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "TRINETRA Hazard Score combines hydrological risk "
        "and local DEM-derived terrain hazard. Satellite "
        "evidence is shown separately as supporting evidence."
    )

    st.divider()

    st.subheader("System Interpretation")

    st.warning(
        f"⚠️ **TRINETRA hazard level: {trinetra_level}.** "
        f"Combined hazard score is **{trinetra_score:.1f}/100**, "
        f"based on hydrological risk (**{hydrological_score:.1f}/100**) "
        f"and local DEM terrain hazard (**{terrain_score:.1f}/100**). "
        "Satellite evidence remains a separate supporting indicator."
    )

    st.write(
        event["system_interpretation"]
    )

    st.divider()

    st.subheader("Satellite Analysis Details")

    s2_col, s1_col = st.columns(2)

    with s2_col:

        st.markdown(
            "### Sentinel-2 Optical Evidence"
        )


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

        st.markdown(
            "### Sentinel-1 SAR Evidence"
        )


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

        st.markdown(
            "### Sentinel-1 SAR Analysis"
        )


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

        st.markdown(
            "### Sentinel-2 Optical Analysis"
        )


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
                "TRINETRA combined hazard",
                "River hydrology model",
                "DEM terrain analysis",
                "Sentinel-2 optical imagery",
                "Sentinel-1 SAR imagery",
            ],
            "Key result": [
                (
                    f"{trinetra_score:.0f}/100 — "
                    f"{trinetra_level}"
                ),
                (
                    f"{hydrological_score:.0f}/100 — "
                    f"{hydrological_level}"
                ),
                (
                    f"{terrain_score:.0f}/100 — "
                    f"{terrain_level}"
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
                "Combined MVP hazard index using hydrological and local DEM terrain components.",
                "Dynamic river-hydrology hazard condition.",
                "Local DEM-derived terrain hazard condition.",
                "Optical satellite evidence for post-event water change.",
                "SAR satellite evidence for post-event water change.",
            ],
        }
    )

    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()


    with st.expander(
        "View complete river dashboard data"
    ):

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


    # ========================================================
    # RAINFALL HAZARD DASHBOARD
    # ========================================================

    st.divider()

    st.title("🌧️ Rainfall Hazard Assessment")


    st.caption(
        "Explainable rainfall-hazard assessment using observed "
        "rainfall, anomaly detection, and next-day forecasting."
    )


    # --------------------------------------------------------
    # Check rainfall files
    # --------------------------------------------------------

    rainfall_files = [
        RAINFALL_HAZARD_PATH,
        RAINFALL_FORECAST_PATH,
        RAINFALL_DAILY_RISK_PATH,
    ]


    missing_rainfall_files = [
        path
        for path in rainfall_files
        if not path.exists()
    ]


    if missing_rainfall_files:

        st.warning(
            "Rainfall dashboard data is incomplete. "
            "Run the rainfall pipeline scripts first."
        )


        for path in missing_rainfall_files:

            st.write(
                f"Missing: `{path}`"
            )


    else:

        rainfall_hazard = load_rainfall_hazard()

        rainfall_forecast = load_rainfall_forecast()

        rainfall_daily = load_rainfall_daily_risk()


        if (
            rainfall_hazard.empty
            or rainfall_forecast.empty
        ):

            st.warning(
                "Rainfall dashboard data is empty."
            )


        else:

            # =================================================
            # LATEST RAINFALL OBSERVATION
            # =================================================

            latest_rainfall = (
                rainfall_hazard
                .sort_values("Date")
                .groupby(
                    "District",
                    as_index=False,
                )
                .tail(1)
                .iloc[0]
            )


            district = str(
                latest_rainfall["District"]
            )


            latest_date = pd.to_datetime(
                latest_rainfall["Date"]
            )


            daily_rainfall = float(
                latest_rainfall["Daily Actual"]
            )


            rainfall_risk_score = float(
                latest_rainfall["risk_score"]
            )


            rainfall_risk_category = str(
                latest_rainfall["risk_category"]
            )


            anomaly_severity = float(
                latest_rainfall["anomaly_severity"]
            )


            # =================================================
            # LATEST OPERATIONAL FORECAST
            # =================================================

            district_forecast = (
                rainfall_forecast[
                    rainfall_forecast["District"]
                    == district
                ]
                .sort_values("Date")
            )


            operational_forecast = (
                district_forecast[
                    district_forecast[
                        "target_rainfall_1d"
                    ].isna()
                ]
                .tail(1)
            )


            if not operational_forecast.empty:

                forecast_row = (
                    operational_forecast.iloc[0]
                )


                forecast_rainfall = float(
                    forecast_row[
                        "predicted_rainfall_1d"
                    ]
                )


                forecast_date = (
                    pd.to_datetime(
                        forecast_row["Date"]
                    )
                    + pd.Timedelta(days=1)
                )


            else:

                forecast_rainfall = None

                forecast_date = None


            # =================================================
            # FORECAST SEVERITY
            # =================================================

            historical_rainfall = (
                rainfall_hazard[
                    "Daily Actual"
                ]
                .dropna()
            )


            q75 = historical_rainfall.quantile(
                0.75
            )


            q90 = historical_rainfall.quantile(
                0.90
            )


            q95 = historical_rainfall.quantile(
                0.95
            )


            if forecast_rainfall is None:

                forecast_severity = 0


            elif forecast_rainfall >= q95:

                forecast_severity = 100


            elif forecast_rainfall >= q90:

                forecast_severity = 70


            elif forecast_rainfall >= q75:

                forecast_severity = 40


            else:

                forecast_severity = 10


            # =================================================
            # NEXT-DAY OPERATIONAL HAZARD
            # =================================================

            operational_hazard_score = (
                0.50 * rainfall_risk_score
                + 0.25 * anomaly_severity
                + 0.25 * forecast_severity
            )


            if operational_hazard_score < 30:

                operational_hazard_category = "LOW"


            elif operational_hazard_score < 60:

                operational_hazard_category = "MODERATE"


            elif operational_hazard_score < 80:

                operational_hazard_category = "HIGH"


            else:

                operational_hazard_category = "CRITICAL"


            # =================================================
            # SELECTED RAINFALL EVENT
            # =================================================

            st.subheader(
                "Selected Rainfall Event"
            )


            rainfall_left, rainfall_right = (
                st.columns(2)
            )


            with rainfall_left:

                st.write(
                    f"**District:** {district}"
                )


                st.write(
                    f"**Latest observation:** "
                    f"{latest_date.strftime('%d %B %Y')}"
                )


            with rainfall_right:

                st.write(
                    f"**Daily rainfall:** "
                    f"{daily_rainfall:.1f} mm"
                )


                if forecast_date is not None:

                    st.write(
                        f"**Forecast date:** "
                        f"{forecast_date.strftime('%d %B %Y')}"
                    )


            # =================================================
            # CURRENT RAINFALL RISK
            # =================================================

            st.subheader(
                "Current Rainfall Risk"
            )


            col1, col2, col3 = (
                st.columns(3)
            )


            # -------------------------------------------------
            # Rainfall risk
            # -------------------------------------------------

            with col1:

                st.metric(
                    "Rainfall Risk Score",
                    f"{rainfall_risk_score:.0f} / 100",
                    border=True,
                )


                st.markdown(
                    f"""
                    <div style="
                        background-color:
                        {risk_color(rainfall_risk_category)};
                        color: white;
                        padding: 10px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        margin-top: 8px;
                    ">
                        {rainfall_risk_category}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            # -------------------------------------------------
            # Anomaly severity
            # -------------------------------------------------

            with col2:

                st.metric(
                    "Anomaly Severity",
                    f"{anomaly_severity:.0f} / 100",
                    border=True,
                )


            # -------------------------------------------------
            # Observed rainfall
            # -------------------------------------------------

            with col3:

                st.metric(
                    "Observed Rainfall",
                    f"{daily_rainfall:.1f} mm",
                    border=True,
                )


            # =================================================
            # NEXT-DAY FORECAST
            # =================================================

            st.subheader(
                "Next-Day Rainfall Forecast"
            )


            forecast_col1, forecast_col2, forecast_col3 = (
                st.columns(3)
            )


            # -------------------------------------------------
            # Predicted rainfall
            # -------------------------------------------------

            with forecast_col1:

                if forecast_rainfall is not None:

                    st.metric(
                        "Predicted Rainfall",
                        f"{forecast_rainfall:.2f} mm",
                        border=True,
                    )

                else:

                    st.metric(
                        "Predicted Rainfall",
                        "N/A",
                        border=True,
                    )


            # -------------------------------------------------
            # Forecast severity
            # -------------------------------------------------

            with forecast_col2:

                st.metric(
                    "Forecast Severity",
                    f"{forecast_severity:.0f} / 100",
                    border=True,
                )


            # -------------------------------------------------
            # Next-day hazard
            # -------------------------------------------------

            with forecast_col3:

                st.metric(
                    "Next-Day Hazard",
                    f"{operational_hazard_score:.1f} / 100",
                    border=True,
                )


            st.markdown(
                f"""
                <div style="
                    background-color:
                    {risk_color(operational_hazard_category)};
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    margin-top: 8px;
                ">
                    NEXT-DAY HAZARD: {operational_hazard_category}
                </div>
                """,
                unsafe_allow_html=True,
            )


            # =================================================
            # RAINFALL INTERPRETATION
            # =================================================

            st.subheader(
                "Rainfall System Interpretation"
            )


            if forecast_rainfall is not None:

                forecast_text = (
                    f"{forecast_rainfall:.2f} mm"
                )

            else:

                forecast_text = "N/A"


            st.info(
                f"""
                **{district} rainfall condition:**

                The latest observed rainfall was
                **{daily_rainfall:.1f} mm**, producing a current
                rainfall risk score of
                **{rainfall_risk_score:.0f}/100
                ({rainfall_risk_category})**.

                The anomaly severity is
                **{anomaly_severity:.0f}/100**.

                The operational model forecasts
                **{forecast_text}**
                for the next day.

                Combining current risk, anomaly severity, and the
                forecast produces a next-day hybrid hazard score of
                **{operational_hazard_score:.1f}/100
                ({operational_hazard_category})**.
                """
            )


            # =================================================
            # RECENT RAINFALL RISK
            # =================================================

            st.subheader(
                "Recent Rainfall Risk"
            )


            recent_daily = (
                rainfall_daily[
                    rainfall_daily["District"]
                    == district
                ]
                .sort_values("date")
                .tail(10)
            )


            if not recent_daily.empty:

                display_columns = [
                    "date",
                    "max_daily_rainfall_mm",
                    "max_risk_score",
                    "risk_category",
                ]


                st.dataframe(
                    recent_daily[
                        display_columns
                    ],
                    use_container_width=True,
                    hide_index=True,
                )


            # =================================================
            # COMPLETE RAINFALL DATA
            # =================================================

            with st.expander(
                "View complete rainfall hazard data"
            ):

                st.dataframe(
                    rainfall_hazard,
                    use_container_width=True,
                    hide_index=True,
                )


    # ========================================================
    # APPLICATION FOOTER
    # ========================================================

    st.divider()

    st.caption(
        "TRINETRA integrates river hydrology, rainfall, DEM-derived "
        "terrain intelligence, and satellite-derived evidence as an "
        "academic disaster-risk assessment prototype. "
        "It is not an official emergency-alert system."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()