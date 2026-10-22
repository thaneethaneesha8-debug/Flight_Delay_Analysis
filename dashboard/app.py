import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Dashboard configuration
st.set_page_config(
    page_title="Flight Delay Analysis",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Flight Delay Analysis Dashboard")
st.markdown(
    "Analyze flight delays, airlines, airports and weather conditions."
)

# Load dataset
file_path = (
    Path(__file__).resolve().parent.parent
    / "dataset"
    / "flight_delay_dataset_cleaned.xlsx"
)

if file_path.exists():
    df = pd.read_excel(file_path)
else:
    uploaded = st.file_uploader(
        "Upload Flight Delay Dataset",
        type=["xlsx", "csv"]
    )

    if uploaded is None:
        st.info("Please upload your Excel or CSV dataset.")
        st.stop()

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

# Prepare data
df.columns = df.columns.str.strip()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["arrival_delay_min"] = pd.to_numeric(
    df["arrival_delay_min"], errors="coerce"
)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

carriers = sorted(df["carrier"].dropna().unique())

selected_carriers = st.sidebar.multiselect(
    "Select Airline",
    carriers,
    default=carriers
)

origins = sorted(df["origin"].dropna().unique())

selected_origins = st.sidebar.multiselect(
    "Select Origin Airport",
    origins,
    default=origins
)

filtered = df[
    df["carrier"].isin(selected_carriers)
    & df["origin"].isin(selected_origins)
].copy()

if filtered.empty:
    st.warning("No flights match your selected filters.")
    st.stop()

# Key Performance Indicators
total_flights = len(filtered)

average_delay = filtered["arrival_delay_min"].mean()

delayed_flights = (
    filtered["delayed_15plus"].eq(1).sum()
)

delay_percentage = (
    delayed_flights / total_flights * 100
    if total_flights else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Flights", total_flights)

c2.metric(
    "Average Arrival Delay",
    f"{average_delay:.1f} min"
    if pd.notna(average_delay) else "N/A"
)

c3.metric(
    "Flights Delayed 15+ Min",
    int(delayed_flights)
)

c4.metric(
    "15+ Min Delay Rate",
    f"{delay_percentage:.1f}%"
)

st.divider()

# 1. Arrival delay distribution
st.subheader("1. Arrival Delay Distribution")

fig = px.histogram(
    filtered,
    x="arrival_delay_min",
    nbins=15,
    title="Distribution of Arrival Delays",
    labels={
        "arrival_delay_min": "Arrival Delay (minutes)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# 2. Average delay by airline
st.subheader("2. Average Delay by Airline")

airline_delay = (
    filtered.groupby("carrier")["arrival_delay_min"]
    .mean()
    .reset_index()
    .sort_values("arrival_delay_min", ascending=False)
)

fig = px.bar(
    airline_delay,
    x="carrier",
    y="arrival_delay_min",
    color="arrival_delay_min",
    title="Average Arrival Delay by Airline",
    labels={
        "carrier": "Airline",
        "arrival_delay_min": "Average Delay (minutes)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# 3. Delay by origin airport
st.subheader("3. Average Delay by Origin Airport")

airport_delay = (
    filtered.groupby("origin")["arrival_delay_min"]
    .mean()
    .reset_index()
    .sort_values("arrival_delay_min", ascending=False)
)

fig = px.bar(
    airport_delay,
    x="origin",
    y="arrival_delay_min",
    title="Average Delay by Departure Airport",
    labels={
        "origin": "Origin Airport",
        "arrival_delay_min": "Average Delay (minutes)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# 4. Delay trend over time
st.subheader("4. Flight Delay Trend")

daily_delay = (
    filtered.dropna(subset=["date"])
    .groupby("date")["arrival_delay_min"]
    .mean()
    .reset_index()
)

fig = px.line(
    daily_delay,
    x="date",
    y="arrival_delay_min",
    markers=True,
    title="Average Arrival Delay Over Time",
    labels={
        "date": "Flight Date",
        "arrival_delay_min": "Average Delay (minutes)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# 5. Delay causes
st.subheader("5. Flight Delay Causes")

if "delay_cause" in filtered.columns:
    cause_data = filtered.dropna(subset=["delay_cause"])

    if not cause_data.empty:
        cause_counts = (
            cause_data["delay_cause"]
            .value_counts()
            .reset_index()
        )

        cause_counts.columns = ["Delay Cause", "Flight Count"]

        fig = px.pie(
            cause_counts,
            names="Delay Cause",
            values="Flight Count",
            title="Recorded Delay Causes"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recorded delay causes in the selected flights.")

# 6. Weather conditions and delay
st.subheader("6. Weather Conditions vs Arrival Delay")

weather_col = st.selectbox(
    "Select Weather Variable",
    [
        "origin_visibility_mi",
        "origin_wind_mph",
        "origin_precip_in"
    ]
)

weather_data = filtered[
    [weather_col, "arrival_delay_min"]
].dropna()

fig = px.scatter(
    weather_data,
    x=weather_col,
    y="arrival_delay_min",
    title=f"{weather_col} vs Arrival Delay",
    labels={
        weather_col: weather_col,
        "arrival_delay_min": "Arrival Delay (minutes)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# 7. Flight records table
st.subheader("7. Flight Details")

st.dataframe(
    filtered,
    use_container_width=True
)

# Download filtered data
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Flight Data",
    data=csv,
    file_name="filtered_flight_delay_data.csv",
    mime="text/csv"
)

st.caption("Flight Delay Analysis | Python, Pandas, Streamlit & Plotly")
