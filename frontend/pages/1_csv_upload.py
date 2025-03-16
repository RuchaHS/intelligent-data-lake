import streamlit as st
import requests
import pandas as pd
import json

st.title("📊 CSV Analysis Dashboard")

BACKEND_URL = "http://localhost:8000/csv"

uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
    st.success("✅ File uploaded successfully!")

    # 🔹 Choose Analysis Type
    analysis_type = st.selectbox("📊 Select an analysis type:", [
        "Metadata Extraction",
        "Anomaly Detection",
        "Data Quality Rules",
        "Vector Search"
    ])

    # ✅ Metadata Extraction
    if analysis_type == "Metadata Extraction":
        if st.button("Extract Metadata"):
            with st.spinner("🔄 Extracting metadata..."):
                response = requests.post(f"{BACKEND_URL}/metadata", files=files)
            if response.status_code == 200:
                metadata = response.json()["metadata"]
                st.json(metadata)
                st.download_button("📥 Download Metadata (JSON)", json.dumps(metadata, indent=4), "metadata.json", "application/json")
            else:
                st.error(response.text)

    # ✅ Anomaly Detection
    elif analysis_type == "Anomaly Detection":
        if st.button("Detect Anomalies"):
            with st.spinner("🔍 Detecting anomalies..."):
                response = requests.post(f"{BACKEND_URL}/detect-anomalies", files=files)
            if response.status_code == 200:
                anomalies_list = response.json().get("anomalies", [])
                if anomalies_list:
                    df_anomalies = pd.DataFrame(anomalies_list)
                    st.subheader("🚨 Detected Anomalies")
                    st.dataframe(df_anomalies)
                    st.download_button("📥 Download Anomalies (CSV)", df_anomalies.to_csv(index=False).encode("utf-8"), "anomalies.csv", "text/csv")
                else:
                    st.success("✅ No anomalies detected.")
            else:
                st.error(response.text)

    # ✅ Data Quality Rules
    elif analysis_type == "Data Quality Rules":
        if st.button("Generate Rules"):
            with st.spinner("🔧 Generating data quality rules..."):
                response = requests.post(f"{BACKEND_URL}/data-quality-rules", files=files)
            if response.status_code == 200:
                rules = response.json()["rules"]
                st.json(rules)
                st.download_button("📥 Download Data Quality Rules (JSON)", json.dumps(rules, indent=4), "data_quality_rules.json", "application/json")
            else:
                st.error(response.text)

    # ✅ Vector Search
    elif analysis_type == "Vector Search":
        query = st.text_input("🔍 Enter search query:")
        if st.button("Perform Vector Search"):
            with st.spinner("🔎 Searching vectors..."):
                response = requests.post(f"{BACKEND_URL}/vector-search", files=files, data={"query": query})
            if response.status_code == 200:
                results = response.json()["results"]
                st.json(results)
                st.download_button("📥 Download Search Results (JSON)", json.dumps(results, indent=4), "vector_search_results.json", "application/json")
            else:
                st.error(response.text)
