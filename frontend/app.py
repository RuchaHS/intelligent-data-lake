import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Intelligent Data Lake", layout="wide")

st.title("📊 Intelligent Data Lake Management")

# Sidebar for navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose a function:", [
    "Text-to-SQL",
    "SQL Explanation",
    "Metadata",
    "Anomaly Detection",
    "Data Profiling",
    "Metadata Detection (LLM)",
    "Data Quality Rules (LLM)"
])

BACKEND_URL = "http://localhost:8000"

# 📌 Text-to-SQL
if option == "Text-to-SQL":
    st.subheader("🔍 Convert Natural Language to SQL")
    query_text = st.text_input("Enter your query:")
    if st.button("Generate SQL"):
        response = requests.post(f"{BACKEND_URL}/text-to-sql", json={"query_text": query_text})
        if response.status_code == 200:
            sql_query = response.json().get("sql_query", "❌ Error generating SQL")
            st.code(sql_query, language="sql")
        else:
            st.error("❌ Error generating SQL")

# 📌 SQL Explanation
elif option == "SQL Explanation":
    st.subheader("📜 Explain SQL Queries")
    sql_query = st.text_area("Paste your SQL query:")
    if st.button("Explain SQL"):
        response = requests.post(f"{BACKEND_URL}/sql-to-text", json={"query_text": sql_query})
        if response.status_code == 200:
            explanation = response.json().get("explanation", "❌ Error explaining SQL")
            st.write(explanation)
        else:
            st.error("❌ Error explaining SQL")

# 📌 Metadata Display - Upload CSV & Show Report
elif option == "Metadata":
    st.subheader("📝 Upload CSV & View Metadata")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Process Metadata"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/upload-metadata", files=files)

            if response.status_code == 200:
                metadata = response.json()
                
                st.subheader("📑 Extracted Metadata")
                # st.json(metadata)

                # ✅ Display Profiling Report (Both Link & Embedded)
                report_url = metadata.get("profiling_report_url")
                if report_url:
                    st.markdown(f"### [📊 View Detailed Data Profiling Report]({BACKEND_URL}{report_url})", unsafe_allow_html=True)
                    # st.components.v1.html(metadata["embedded_report"], height=600) #to embed html into current page
                else:
                    st.error("❌ Profiling report not available.")
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

elif option == "Anomaly Detection":
    st.subheader("🚨 Detect Anomalies in Data")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        if st.button("Detect Anomalies"):
            # ✅ Send the file to FastAPI
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/detect-anomalies", files=files)

            if response.status_code == 200:
                result = response.json()
                anomaly_csv_url = result.get("anomaly_csv_url")

                if anomaly_csv_url:
                    # ✅ Provide Download Option for Anomaly CSV
                    st.markdown(
                        f'<h3 style="color:#333;">📥 <a href="{BACKEND_URL}{anomaly_csv_url}" download="anomalies.csv" target="_blank">Download Anomalies CSV</a></h3>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("No anomalies detected.")
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

# NEW FEATURES
elif option == "Metadata Detection (LLM)":
    st.subheader("📄 AI-Powered Metadata Insights")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Analyze with AI"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/metadata-llm", files=files)

            if response.status_code == 200:
                metadata = response.json()
                st.markdown("### 📊 AI-Generated Metadata Analysis")
                st.write(metadata["metadata_analysis"])
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")


elif option == "Data Quality Rules (LLM)":
    st.subheader("🛡️ AI-Powered Data Quality Rules")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Generate Data Quality Rules"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/data-quality-rules", files=files)

            if response.status_code == 200:
                rules_json = response.json()
                st.markdown("### 📜 Suggested Data Quality Rules")
                st.json(rules_json)

                st.download_button(
                    label="📥 Download Data Quality Rules JSON",
                    data=str(rules_json),
                    file_name="data_quality_rules.json",
                    mime="application/json"
                )
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")


