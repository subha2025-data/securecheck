# app.py (SecureCheck Multi-Page Version)
import streamlit as st
import pandas as pd
from db_connection import get_engine  # ✅ Ensure this file returns SQLAlchemy engine

# ✅ Utility: Read from a SQL View
def run_view(view_name):
    try:
        engine = get_engine()
        query = f"SELECT * FROM {view_name}"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return pd.DataFrame()

# ✅ App Layout Config
st.set_page_config(page_title="SecureCheck Dashboard", layout="wide")
st.sidebar.title("📌 SecureCheck Navigation")
page = st.sidebar.radio("Choose a section:", (
    "📊 Reports Dashboard",
    "🚨 High-Risk Vehicle Alert",
    "⏱️ Time-Based Trends",
    "🌍 Country-Wise Logs"
))

# --- Page 1: Reports Dashboard ---
if page == "📊 Reports Dashboard":
    st.title("📊 Explore Reports")
    query_views = {
        "🚗 Top 10 vehicle numbers in drug-related stops": "top_10_drug_vehicles",
        "🚓 Most frequently searched vehicles": "most_searched_vehicles",
        "🢍 Driver age with highest arrest rate": "age_group_highest_arrest",
        "🌍 Gender distribution by country": "gender_distribution_by_country",
        "🔍 Race & gender with highest search rate": "search_rate_race_gender",
        "🕒 Time of day with most traffic stops": "stops_by_time",
        "🕘 Avg stop duration by violation": "avg_stop_duration_by_violation",
        "🌃 Night vs Day arrest rate": "night_arrest_comparison",
        "⚖️ Violations with high search/arrest": "violation_search_arrest_rate",
        "🧑‍🏫 Common violations (<25 age)": "young_driver_violations",
        "📉 Rarely searched/arrested violations": "rare_violation_cases",
        "🌐 Countries with most drug stops": "drug_stops_by_country",
        "🇨🇳 Arrest rate by country & violation": "arrest_by_country_violation",
        "🏳️ Country with most searches": "country_most_searches",
        "📆 Yearly stops & arrests by country": "yearly_country_arrest_stats",
        "📊 Violation trends by age & race": "age_race_violation_trends",
        "⏳ Stop time breakdown (year/month/hour)": "stop_time_breakdown",
        "📈 Violation rank by search/arrest rate": "violation_search_arrest_ranked",
        "🌎 Driver demographics by country": "driver_demographics_by_country",
        "🏆 Top 5 violations by arrest rate": "top_5_arrest_rate_violations"
    }
    selected_query = st.selectbox("Select a report to view:", list(query_views.keys()))
    if selected_query:
        view_name = query_views[selected_query]
        df = run_view(view_name)
        st.dataframe(df, use_container_width=True)

# --- Page 2: High-Risk Vehicle Alert ---
elif page == "🚨 High-Risk Vehicle Alert":
    st.title("🚨 Vehicle Alert System")

    engine = get_engine()
    vehicle_options = pd.read_sql_query("SELECT DISTINCT vehicle_number FROM traffic_data", engine)
    selected_vehicle = st.selectbox("Select a vehicle number to check:", vehicle_options['vehicle_number'])

    if selected_vehicle:
        alert_query = f"""
            SELECT 1 FROM high_risk_vehicles WHERE vehicle_number = '{selected_vehicle}'
        """
        alert_df = pd.read_sql_query(alert_query, engine)

        if not alert_df.empty:
            st.error("🚨 ALERT: High-risk vehicle flagged in drug-related activity!")
        else:
            st.success("✅ Vehicle is clean.")

# --- Page 4: Time-Based Trends ---
elif page == "⏱️ Time-Based Trends":
    st.title("⏱️ Stop Distribution by Hour")
    time_df = run_view("stop_time_analysis")
    st.bar_chart(time_df.set_index("hour"))

# --- Page 5: Country-Level Logs ---
elif page == "🌍 Country-Wise Logs":
    st.title("🌍 Central Control - Logs by Country")
    location_df = run_view("stop_by_location")
    selected_country = st.selectbox("Select a country:", location_df['country_name'])

    if selected_country:
        query = f"""
            SELECT * FROM traffic_data
            WHERE country_name = '{selected_country}'
            LIMIT 100
        """
        engine = get_engine()
        data = pd.read_sql_query(query, engine)
        st.dataframe(data)
