import streamlit as st
import requests
import pandas as pd
import json
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.io as pio

BACKEND_URL = "http://localhost:8000/db"

def run():
    """Runs the DuckDB Integration Dashboard"""
    st.title("🛢 Analysis & Insights")

    # ✅ Select Database Operation
    operation = st.selectbox("📊 Choose an operation:", [
        "Extract Metadata",
        "Anomaly Detection",
        "Data Profiling",
        "Data Quality Rules"
    ])

    tables_response = requests.get(f"{BACKEND_URL}/list-tables")

    if tables_response.status_code == 200:
        tables = tables_response.json()["tables"]
        selected_table = st.selectbox("📌 Select a table:", ["(Choose a table)"] + tables)

        if selected_table != "(Choose a table)":
            st.subheader(f"📋 Table Preview: `{selected_table}`")
            preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
            if preview_response.status_code == 200:
                df_preview = pd.DataFrame(preview_response.json()["preview"])
                
                # ✅ Fix: Replace null values for proper rendering
                df_preview.fillna("N/A", inplace=True)  # Replace "null" with "N/A"
    
                st.dataframe(df_preview)
    
    # ✅ Metadata Extraction
    if operation == "Extract Metadata":

        if st.button("Extract Metadata"):
            with st.spinner("🔍 Extracting metadata..."):
                response = requests.get(f"{BACKEND_URL}/extract-metadata/{selected_table}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(response.text)

    # ✅ Anomaly Detection
    elif operation == "Anomaly Detection":

        if st.button("Detect Anomalies"):
            with st.spinner("🔍 Detecting Anomalies..."):
                response = requests.get(f"{BACKEND_URL}/detect-anomalies/{selected_table}")
            
            if response.status_code == 200:
                response_data = response.json()
                anomalies = response_data.get("anomalies", [])
                summary = response_data.get("summary", {})
                visualization_json = response_data.get("visualization", None)

                if anomalies:
                    df_anomalies = pd.DataFrame(anomalies)
                    st.subheader("🚨 Anomaly Detection Results")
                    st.dataframe(df_anomalies)

                    # ✅ Display Explanation Summary
                    if summary:
                        st.markdown("### 📄 Explanation of Anomalies")
                        st.markdown(f"**Total Records:** {summary.get('total_records', 'N/A')}")
                        st.markdown(f"**Anomalies Detected:** {summary.get('anomalies_detected', 'N/A')}")
                        st.markdown(f"**Anomaly Percentage:** {summary.get('anomaly_percentage', 'N/A')}%")
                        st.info(summary.get("message", "No detailed explanation available."))

                    # ✅ Display Plotly Graph
                    if visualization_json:
                        fig = pio.from_json(visualization_json)
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    st.success("✅ No anomalies detected.")
            else:
                st.error(response.text)


    elif operation == "Data Profiling":

        if st.button("Generate Data Profile"):
            with st.spinner("🔍 Generating data profile..."):
                response = requests.get(f"{BACKEND_URL}/profile-data/{selected_table}")

            if response.status_code == 200:
                profiling_data = response.json()
                html_report_path = profiling_data.get("html_report")
                json_report_path = profiling_data.get("json_report")

                if html_report_path and json_report_path:
                    st.success("✅ Data profiling completed!")

                    # ✅ Display download & view options
                    st.markdown("### 📥 Download & View Profiling Report")
                    html_download_url = f"{BACKEND_URL}/download-profile-report/{selected_table}/html"
                    json_download_url = f"{BACKEND_URL}/download-profile-report/{selected_table}/json"
                    view_report_url = f"{BACKEND_URL}/view-profile-report/{selected_table}"

                    st.markdown(f"📄 [Download as HTML]({html_download_url})", unsafe_allow_html=True)
                    st.markdown(f"📜 [Download as JSON]({json_download_url})", unsafe_allow_html=True)

                    # ✅ Embed Report in Streamlit UI using iframe
                    st.markdown("### 🌐 Interactive Report")
                    components.iframe(view_report_url, height=1200, scrolling=True)  # ✅ Display HTML report in iframe
                else:
                    st.warning("⚠️ Profiling report paths not available.")
            else:
                st.error(f"🚨 Error: {response.text}")

    # ✅ Data Quality Rules
    elif operation == "Data Quality Rules":

        if st.button("Generate Rules"):
            with st.spinner("🔍Recommending data quality rules.."):
                response = requests.get(f"{BACKEND_URL}/data-quality-rules/{selected_table}")
                print(response)

            if response.status_code == 200:
                rules = response.json()["rules"]
                st.json(rules)
            else:
                st.error(response.text)


# ✅ Ensure the script runs only when executed directly
if __name__ == "__main__":
    run()