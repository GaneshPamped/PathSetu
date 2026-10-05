import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PATHSETU - AI-Based Disaster-Aware Accessibility System
# ---------------------------------------------------------

st.set_page_config(
    page_title="PathSetu",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

@st.cache_data
def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except Exception:
        return None


def show_dataframe(df, height=400):
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=height)
    else:
        st.warning("No data available for this section.")


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

road_data = load_csv("pathsetu_final_road_dataset.csv")
village_data = load_csv("pathsetu_final_village_dataset.csv")
weather_data = load_csv("weather.csv")
weather_features = load_csv("weather_features.csv")
landslides = load_csv("landslides.csv")
routes = load_csv("risk_aware_routes.csv")
supply = load_csv("supply_priorities.csv")
isolation = load_csv("village_isolation.csv")
simulation = load_csv("disaster_simulation.csv")
field_reports = load_csv("field_reports.csv")
road_landslide = load_csv("road_landslide_features.csv")
road_terrain = load_csv("road_terrain.csv")


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("🛣️ PathSetu")

st.sidebar.markdown(
    """
    **AI-Based Disaster-Aware Accessibility
    and Supply Routing System**

    **Pilot Region:** Gangtok, Sikkim  
    **Focus:** North-East India
    """
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "🗺️ Risk Map",
        "🌦️ Weather",
        "🛣️ Road Risk",
        "🏘️ Village Isolation",
        "🚑 Risk-Aware Routes",
        "📦 Supply Priorities",
        "🌋 Disaster Simulator",
        "📋 Field Reports",
        "📊 System Statistics",
        "📖 Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.caption("PathSetu • Disaster-Aware Accessibility")

# ---------------------------------------------------------
# PATHSETU AI ASSISTANT
# ---------------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader("🤖 PathSetu AI Assistant")

chat_question = st.sidebar.text_input(
    "Ask PathSetu",
    placeholder="e.g. Which villages are isolated?"
)


def pathsetu_assistant(question):
    q = question.lower().strip()

    # -----------------------------------------
    # Village isolation
    # -----------------------------------------
    if "village" in q and (
        "isolat" in q or
        "access" in q or
        "cut off" in q
    ):

        data = village_data if village_data is not None else isolation

        if data is None:
            return "Village isolation data is not available."

        priority_col = None

        for col in ["priority", "isolation_level", "risk_level"]:
            if col in data.columns:
                priority_col = col
                break

        if priority_col:
            high = data[
                data[priority_col]
                .astype(str)
                .str.upper()
                .isin(["HIGH", "VERY HIGH", "MODERATE"])
            ]

            if not high.empty:
                names = []

                for col in ["village", "village_name", "name"]:
                    if col in high.columns:
                        names = high[col].astype(str).head(10).tolist()
                        break

                if names:
                    return (
                        "Based on the available PathSetu village dataset, "
                        "the following villages require attention: "
                        + ", ".join(names)
                    )

        return (
            f"PathSetu currently has {len(data)} village records "
            "available for accessibility analysis."
        )

    # -----------------------------------------
    # Road risk
    # -----------------------------------------
    if (
        "road" in q
        and ("risk" in q or "danger" in q or "hazard" in q)
    ):

        if road_data is None:
            return "Road risk data is not available."

        risk_col = None

        for col in [
            "risk_score",
            "risk",
            "road_risk",
            "risk_value"
        ]:
            if col in road_data.columns:
                risk_col = col
                break

        if risk_col:

            values = pd.to_numeric(
                road_data[risk_col],
                errors="coerce"
            ).dropna()

            if not values.empty:

                return (
                    f"The PathSetu road dataset contains "
                    f"{len(road_data):,} road records. "
                    f"The average risk score is "
                    f"{values.mean():.2f}, while the maximum "
                    f"recorded score is {values.max():.2f}."
                )

        return (
            f"PathSetu contains {len(road_data):,} road records."
        )

    # -----------------------------------------
    # Weather
    # -----------------------------------------
    if (
        "weather" in q
        or "rain" in q
        or "rainfall" in q
    ):

        if weather_data is None:
            return "Weather data is not available."

        return (
            f"PathSetu has {len(weather_data):,} weather records. "
            "The dashboard Weather section provides the available "
            "weather and rainfall information."
        )

    # -----------------------------------------
    # Routes
    # -----------------------------------------
    if (
        "route" in q
        or "routing" in q
        or "safer" in q
        or "safe route" in q
    ):

        if routes is None:
            return "Risk-aware route data is not available."

        return (
            f"PathSetu contains {len(routes):,} risk-aware route "
            "records. These routes consider disaster-related "
            "road risk rather than distance alone."
        )

    # -----------------------------------------
    # Supplies
    # -----------------------------------------
    if (
        "supply" in q
        or "supplies" in q
        or "priority" in q
        or "emergency" in q
    ):

        if supply is None:
            return "Supply priority data is not available."

        return (
            f"PathSetu has {len(supply):,} supply-priority records. "
            "Open the Supply Priorities section to inspect the "
            "village-level prioritization."
        )

    # -----------------------------------------
    # Disaster simulation
    # -----------------------------------------
    if (
        "disaster" in q
        or "closure" in q
        or "closed" in q
        or "simulation" in q
        or "what if" in q
    ):

        if simulation is None:
            return "Disaster simulation data is not available."

        return (
            f"The disaster simulator contains {len(simulation):,} "
            "simulation records. It evaluates how road disruption "
            "can affect accessibility and villages."
        )

    # -----------------------------------------
    # Landslides
    # -----------------------------------------
    if (
        "landslide" in q
        or "landslides" in q
    ):

        if landslides is None:
            return "Landslide data is not available."

        return (
            f"The PathSetu dataset contains "
            f"{len(landslides):,} historical landslide records."
        )

    # -----------------------------------------
    # Help
    # -----------------------------------------
    if (
        "help" in q
        or "what can you do" in q
        or "hello" in q
        or "hi" == q
    ):

        return (
            "I'm the PathSetu AI Assistant. You can ask me about "
            "road risk, villages, weather, safer routes, emergency "
            "supplies, landslides, or disaster simulations."
        )

    # -----------------------------------------
    # Default response
    # -----------------------------------------

    return (
        "I can help with PathSetu road risk, village isolation, "
        "weather, risk-aware routes, supply priorities, landslides "
        "and disaster simulations. Try asking something like: "
        "\"Which roads have high risk?\""
    )


if chat_question:

    answer = pathsetu_assistant(chat_question)

    st.sidebar.success(answer)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🛣️ PathSetu")

st.markdown(
    """
    ### AI-Based Disaster-Aware Accessibility and Supply Routing System

    A decision-support platform for identifying **road risk, village
    isolation, safer routes, supply priorities, and disaster impacts**
    in mountainous regions.
    """
)

st.divider()


# =========================================================
# OVERVIEW
# =========================================================

if page == "🏠 Overview":

    st.header("🏠 PathSetu Overview")

    st.markdown(
        """
        PathSetu combines road-network information, rainfall,
        terrain characteristics, landslide history, village
        accessibility and disaster simulations to support
        disaster-aware transportation planning.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    road_count = len(road_data) if road_data is not None else 0
    village_count = len(village_data) if village_data is not None else 0
    landslide_count = len(landslides) if landslides is not None else 0
    route_count = len(routes) if routes is not None else 0

    col1.metric("Road Records", f"{road_count:,}")
    col2.metric("Village Records", f"{village_count:,}")
    col3.metric("Landslide Records", f"{landslide_count:,}")
    col4.metric("Route Records", f"{route_count:,}")

    st.subheader("🎯 Core Capabilities")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            **🌧️ Disaster Risk**

            Combines rainfall, terrain slope and
            historical landslide information.
            """
        )

    with c2:
        st.markdown(
            """
            **🚑 Risk-Aware Routing**

            Identifies routes that can reduce
            exposure to hazardous road segments.
            """
        )

    with c3:
        st.markdown(
            """
            **🏘️ Accessibility**

            Identifies villages that may become
            isolated during disruption.
            """
        )

    st.subheader("📍 Pilot Region")

    st.info(
        "PathSetu is demonstrated using the Gangtok / Sikkim region "
        "with emphasis on mountainous road accessibility and "
        "disaster-aware transportation."
    )


# =========================================================
# RISK MAP
# =========================================================

elif page == "🗺️ Risk Map":

    st.header("🗺️ PathSetu Risk Map")

    map_file = DATA_DIR / "pathsetu_risk_map.html"

    if map_file.exists():

        st.markdown(
            "Interactive risk map generated from the PathSetu road network."
        )

        html = map_file.read_text(encoding="utf-8")

        st.components.v1.html(
            html,
            height=700,
            scrolling=True
        )

    else:
        st.warning("Risk map HTML file was not found.")


# =========================================================
# WEATHER
# =========================================================

elif page == "🌦️ Weather":

    st.header("🌦️ Weather & Rainfall")

    if weather_data is not None:

        st.subheader("Latest Weather Dataset")

        st.dataframe(
            weather_data.tail(20),
            use_container_width=True
        )

        numeric_cols = weather_data.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:

            selected = st.selectbox(
                "Select a weather variable",
                numeric_cols
            )

            chart_data = weather_data[[selected]].dropna()

            if not chart_data.empty:
                st.line_chart(chart_data)

    else:
        st.warning("Weather dataset unavailable.")

    if weather_features is not None:

        st.subheader("🌧️ Rainfall Features")

        st.dataframe(
            weather_features.tail(20),
            use_container_width=True
        )


# =========================================================
# ROAD RISK
# =========================================================

elif page == "🛣️ Road Risk":

    st.header("🛣️ Road Risk Analysis")

    if road_data is None:
        st.error("Final road dataset not found.")
    else:

        st.write(
            f"Dataset contains **{len(road_data):,} road records**."
        )

        risk_column = None

        for column in [
            "risk_score",
            "risk",
            "road_risk",
            "risk_value"
        ]:
            if column in road_data.columns:
                risk_column = column
                break

        if risk_column:

            values = pd.to_numeric(
                road_data[risk_column],
                errors="coerce"
            ).dropna()

            if not values.empty:

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Average Risk",
                    f"{values.mean():.2f}"
                )

                c2.metric(
                    "Maximum Risk",
                    f"{values.max():.2f}"
                )

                c3.metric(
                    "Minimum Risk",
                    f"{values.min():.2f}"
                )

        st.subheader("Road Risk Dataset")

        show_dataframe(road_data)


# =========================================================
# VILLAGE ISOLATION
# =========================================================

elif page == "🏘️ Village Isolation":

    st.header("🏘️ Village Isolation")

    data = village_data if village_data is not None else isolation

    if data is None:
        st.warning("Village isolation data unavailable.")

    else:

        st.write(
            f"Analysed **{len(data):,} village records**."
        )

        st.dataframe(
            data,
            use_container_width=True,
            height=500
        )

        if "priority" in data.columns:

            st.subheader("Priority Distribution")

            counts = (
                data["priority"]
                .astype(str)
                .value_counts()
            )

            st.bar_chart(counts)


# =========================================================
# RISK AWARE ROUTES
# =========================================================

elif page == "🚑 Risk-Aware Routes":

    st.header("🚑 Risk-Aware Routing")

    st.markdown(
        """
        PathSetu compares normal road routing with
        risk-aware alternatives to identify routes that
        can reduce exposure to hazardous segments.
        """
    )

    if routes is not None:

        st.write(
            f"Available route records: **{len(routes):,}**"
        )

        st.dataframe(
            routes,
            use_container_width=True,
            height=500
        )

    else:
        st.warning("Risk-aware route dataset unavailable.")


# =========================================================
# SUPPLY PRIORITIES
# =========================================================

elif page == "📦 Supply Priorities":

    st.header("📦 Emergency Supply Prioritization")

    st.markdown(
        """
        This section identifies villages that should receive
        greater attention during disaster-response planning
        based on accessibility and risk indicators.
        """
    )

    if supply is not None:

        st.dataframe(
            supply,
            use_container_width=True,
            height=500
        )

        if "priority" in supply.columns:

            st.subheader("Priority Distribution")

            st.bar_chart(
                supply["priority"]
                .astype(str)
                .value_counts()
            )

    else:
        st.warning("Supply priority dataset unavailable.")


# =========================================================
# DISASTER SIMULATOR
# =========================================================

elif page == "🌋 Disaster Simulator":

    st.header("🌋 Disaster What-If Simulator")

    st.markdown(
        """
        The simulator evaluates the potential impact of road
        disruptions and identifies villages that could experience
        increased travel difficulty.
        """
    )

    if simulation is not None:

        st.subheader("Simulation Results")

        st.dataframe(
            simulation,
            use_container_width=True,
            height=500
        )

        numeric_cols = simulation.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:

            selected = st.selectbox(
                "Select impact variable",
                numeric_cols
            )

            st.bar_chart(
                simulation[selected].dropna()
            )

    else:
        st.warning("Disaster simulation dataset unavailable.")


# =========================================================
# FIELD REPORTS
# =========================================================

elif page == "📋 Field Reports":

    st.header("📋 Field Reports")

    st.warning(
        "Important: the available field reports are "
        "DEMONSTRATION records and should not be interpreted "
        "as verified real-time observations."
    )

    if field_reports is not None:

        st.dataframe(
            field_reports,
            use_container_width=True,
            height=500
        )

    else:
        st.warning("Field report dataset unavailable.")


# =========================================================
# SYSTEM STATISTICS
# =========================================================

elif page == "📊 System Statistics":

    st.header("📊 PathSetu System Statistics")

    datasets = {
        "Final Road Dataset": road_data,
        "Final Village Dataset": village_data,
        "Weather": weather_data,
        "Historical Weather Features": weather_features,
        "Landslides": landslides,
        "Risk-Aware Routes": routes,
        "Supply Priorities": supply,
        "Village Isolation": isolation,
        "Disaster Simulation": simulation,
        "Field Reports": field_reports,
        "Road-Landslide Features": road_landslide,
        "Road Terrain": road_terrain,
    }

    rows = []

    for name, df in datasets.items():

        rows.append(
            {
                "Dataset": name,
                "Available": "Yes" if df is not None else "No",
                "Rows": len(df) if df is not None else 0,
                "Columns": len(df.columns) if df is not None else 0
            }
        )

    stats = pd.DataFrame(rows)

    st.dataframe(
        stats,
        use_container_width=True
    )


# =========================================================
# METHODOLOGY
# =========================================================

elif page == "📖 Methodology":

    st.header("📖 PathSetu Methodology")

    st.subheader("Risk Model")

    st.markdown(
        """
        PathSetu combines three major components:

        **1. Rainfall Risk — 40%**

        - 24-hour rainfall
        - 72-hour rainfall
        - 7-day rainfall

        **2. Terrain Slope — 25%**

        Steeper road segments receive higher terrain-risk
        contribution.

        **3. Historical Landslide Risk — 35%**

        Based on proximity and historical landslide occurrence.

        The combined score is classified into:

        - 🟢 LOW
        - 🟡 MODERATE
        - 🟠 HIGH
        - 🔴 VERY HIGH
        """
    )

    st.subheader("Risk-Aware Routing")

    st.markdown(
        """
        Instead of considering only distance, PathSetu
        incorporates road-risk information when evaluating
        alternative routes.

        The objective is to identify routes that can reduce
        disaster exposure while keeping additional travel
        distance reasonable.
        """
    )

    st.subheader("Disaster Simulation")

    st.markdown(
        """
        The disaster simulator performs what-if road closure
        analysis to identify potentially isolated villages and
        estimate changes in accessibility.
        """
    )

    st.subheader("Scope")

    st.info(
        "PathSetu is a research and decision-support prototype. "
        "It should not be treated as an operational emergency "
        "dispatch or life-safety system without validation using "
        "authoritative real-time data."
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "PathSetu | AI-Based Disaster-Aware Accessibility and "
    "Supply Routing System for North-East India"
)