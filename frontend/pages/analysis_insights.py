import streamlit as st
import requests
import pandas as pd
import json
import streamlit.components.v1 as components

# ✅ Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="🛢 Analysis / Insights", layout="wide")

BACKEND_URL = "http://localhost:8000/db"

def run():
    """Runs the DuckDB Integration Dashboard"""
    st.title("🛢 DuckDB Integration Dashboard")

    # ✅ Select Database Operation
    operation = st.selectbox("📊 Choose an operation:", [
        "Extract Metadata",
        "Anomaly Detection",
        "Data Profiling",  # ✅ Added Data Profiling Feature
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


    elif operation == "Data Profiling":
        table_name = st.text_input("Enter Table Name:")

        if st.button("Generate Data Profile"):
            with st.spinner("🔍 Generating data profile..."):
                response = requests.get(f"{BACKEND_URL}/profile-data/{table_name}")

            if response.status_code == 200:
                profiling_data = response.json()
                html_report_path = profiling_data.get("html_report")
                json_report_path = profiling_data.get("json_report")

                if html_report_path and json_report_path:
                    st.success("✅ Data profiling completed!")

                    # ✅ Display download & view options
                    st.markdown("### 📥 Download & View Profiling Report")
                    html_download_url = f"{BACKEND_URL}/download-profile-report/{table_name}/html"
                    json_download_url = f"{BACKEND_URL}/download-profile-report/{table_name}/json"
                    view_report_url = f"{BACKEND_URL}/view-profile-report/{table_name}"

                    st.markdown(f"📄 [Download as HTML]({html_download_url})", unsafe_allow_html=True)
                    st.markdown(f"📜 [Download as JSON]({json_download_url})", unsafe_allow_html=True)

                    # ✅ Embed Report in Streamlit UI using iframe
                    st.markdown("### 🌐 Interactive Report")
                    components.iframe(view_report_url, height=1000, scrolling=True)  # ✅ Display HTML report in iframe
                else:
                    st.warning("⚠️ Profiling report paths not available.")
            else:
                st.error(f"🚨 Error: {response.text}")

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

# ✅ Ensure the script runs only when executed directly
if __name__ == "__main__":
    run()