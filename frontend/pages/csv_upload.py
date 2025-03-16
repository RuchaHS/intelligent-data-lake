import streamlit as st
import requests
import pandas as pd
import json

BACKEND_URL = "http://localhost:8000/csv"

def run():
    st.title("📊 Upload & Analyze CSV")

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

        if st.button("Run Analysis"):
            with st.spinner("🔄 Processing..."):
                response = requests.post(f"{BACKEND_URL}/{analysis_type.lower().replace(' ', '-')}", files=files)

            if response.status_code == 200:
                results = response.json()
                st.json(results)
                st.download_button("📥 Download Results (JSON)", json.dumps(results, indent=4), "results.json", "application/json")
            else:
                st.error(response.text)