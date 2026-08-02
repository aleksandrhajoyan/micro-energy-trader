import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

# Page setup
st.set_page_config(
    page_title="Micro Energy Trader Dashboard",
    page_icon="⚡",
    layout="wide",
)

# Database Connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@timescaledb:5432/energy_db"
)


@st.cache_resource
def get_db_engine():
    return create_engine(DATABASE_URL)


engine = get_db_engine()

# Title and Auto-refresh
st.title("⚡ Micro Energy Trader — Monitoring Dashboard")
st.markdown("Real-time monitoring of weather metrics and AI trading decisions.")

if st.button("🔄 Refresh Data"):
    st.rerun()

# ---------------------------------------------------------
# SECTION 1: Weather Metrics (TimescaleDB)
# ---------------------------------------------------------
st.header("📊 Weather Metrics History")

try:
    weather_query = """
        SELECT time, temperature, wind_speed, cloud_cover, solar_irradiance 
        FROM weather_metrics 
        ORDER BY time DESC 
        LIMIT 50;
    """
    df_weather = pd.read_sql_query(weather_query, engine)

    if not df_weather.empty:
        # Key Metrics Row
        latest = df_weather.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature (°C)", f"{latest['temperature']:.1f}")
        col2.metric("Solar Irradiance (W/m²)", f"{latest['solar_irradiance']:.1f}")
        col3.metric("Wind Speed (m/s)", f"{latest['wind_speed']:.1f}")
        col4.metric("Cloud Cover (%)", f"{latest['cloud_cover']:.1f}")

        # Charts
        col_left, col_right = st.columns(2)

        with col_left:
            fig_solar = px.line(
                df_weather,
                x="time",
                y="solar_irradiance",
                title="Solar Irradiance Over Time",
                markers=True,
            )
            st.plotly_chart(fig_solar, use_container_width=True)

        with col_right:
            fig_wind = px.line(
                df_weather,
                x="time",
                y="wind_speed",
                title="Wind Speed Over Time",
                markers=True,
            )
            st.plotly_chart(fig_wind, use_container_width=True)
    else:
        st.info("No weather metrics recorded yet. Trigger n8n workflow to generate data.")

except Exception as e:
    st.error(f"Error fetching weather metrics: {e}")

# ---------------------------------------------------------
# SECTION 2: AI Trading Decisions
# ---------------------------------------------------------
st.header("🤖 AI Agent Trading Decisions")

try:
    decisions_query = """
        SELECT id, thread_id, action, decision_data, created_at 
        FROM trading_decisions 
        ORDER BY created_at DESC 
        LIMIT 20;
    """
    df_decisions = pd.read_sql_query(decisions_query, engine)

    if not df_decisions.empty:
        st.dataframe(
            df_decisions[["created_at", "action", "thread_id", "decision_data"]],
            use_container_width=True,
        )
    else:
        st.info("No trading decisions recorded yet.")

except Exception as e:
    st.error(f"Error fetching trading decisions: {e}")