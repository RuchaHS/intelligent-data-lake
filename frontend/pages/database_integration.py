import streamlit as st
import requests
import pandas as pd
import json

st.title("🛢 DuckDB Integration Dashboard")

BACKEND_URL = "http://localhost:8000/db"

# ✅ Select Database Operation
operation = st.selectbox("📊 Choose an operation:", [
    "Extract Metadata",
    "Anomaly Detection",
    "Data Profiling",
    "Data Quality Rules",
    "Optimize Query",
    "Vector Search"
])

# ✅ Metadata Extraction
if operation == "Extract Metadata":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Extract Metadata"):
        response = requests.get(f"{BACKEND_URL}/extract-metadata/{table_name}")
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(response.text)

# ✅ Anomaly Detection
elif operation == "Anomaly Detection":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Detect Anomalies"):
        response = requests.get(f"{BACKEND_URL}/detect-anomalies/{table_name}")
        if response.status_code == 200:
            anomalies = response.json().get("anomalies", [])
            if anomalies:
                df_anomalies = pd.DataFrame(anomalies)
                st.dataframe(df_anomalies)
            else:
                st.success("✅ No anomalies detected.")
        else:
            st.error(response.text)

# ✅ Data Profiling (Newly Added)
elif operation == "Data Profiling":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Generate Data Profile"):
        response = requests.get(f"{BACKEND_URL}/profile-data/{table_name}")
        if response.status_code == 200:
            profile_report = response.json().get("profiling_report", None)
            if profile_report:
                st.success("✅ Data profiling completed!")
                st.markdown(f"[📊 View Data Profiling Report]({profile_report})", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No profiling report found.")
        else:
            st.error(response.text)

# ✅ Data Quality Rules
elif operation == "Data Quality Rules":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Generate Rules"):
        response = requests.get(f"{BACKEND_URL}/data-quality-rules/{table_name}")
        if response.status_code == 200:
            rules = response.json()["rules"]
            st.json(rules)
        else:
            st.error(response.text)

# ✅ Query Optimization
elif operation == "Optimize Query":
    query_text = st.text_area("Enter SQL Query:")
    if st.button("Optimize Query"):
        response = requests.post(f"{BACKEND_URL}/optimize-query", data={"query_text": query_text})
        if response.status_code == 200:
            st.text_area("Optimized Query:", response.json()["optimized_query"])
        else:
            st.error(response.text)

# ✅ Vector Search
elif operation == "Vector Search":
    table_name = st.text_input("Enter Table Name:")
    query = st.text_input("Enter Search Query:")
    if st.button("Perform Vector Search"):
        response = requests.get(f"{BACKEND_URL}/vector-search/{table_name}", params={"query": query})
        if response.status_code == 200:
            st.json(response.json()["results"])
        else:
            st.error(response.text)