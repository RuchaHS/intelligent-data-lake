import streamlit as st
import requests

st.set_page_config(page_title="Intelligent Data Lake", layout="wide")

st.title("📊 Intelligent Data Lake Management")

# Sidebar for navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose a function:", ["Text-to-SQL", "SQL Explanation", "Metadata", "Anomaly Detection"])

BACKEND_URL = "http://localhost:8000"

# 📌 Text-to-SQL
if option == "Text-to-SQL":
    st.subheader("🔍 Convert Natural Language to SQL")
    query_text = st.text_input("Enter your query:")
    if st.button("Generate SQL"):
        response = requests.post(f"{BACKEND_URL}/text-to-sql", json={"query_text": query_text})
        sql_query = response.json().get("sql_query", "❌ Error generating SQL")
        st.code(sql_query, language="sql")

# 📌 SQL Explanation
elif option == "SQL Explanation":
    st.subheader("📜 Explain SQL Queries")
    sql_query = st.text_area("Paste your SQL query:")
    if st.button("Explain SQL"):
        response = requests.post(f"{BACKEND_URL}/sql-to-text", json={"query_text": sql_query})
        explanation = response.json().get("explanation", "❌ Error explaining SQL")
        st.write(explanation)
# 📌 Metadata Display - Upload CSV & Show Report
if option == "Metadata":
    st.subheader("📝 Upload CSV & View Metadata")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        if st.button("Process Metadata"):
            # ✅ Send the file to FastAPI
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/upload-metadata", files=files)

            if response.status_code == 200:
                metadata = response.json()

                st.subheader("📑 Extracted Metadata")
                st.json(metadata)

                # ✅ Display Profiling Report Link
                report_path = metadata.get("profiling_report")
                if report_path:
                    st.markdown(f"[📊 View Data Profiling Report]({report_path})", unsafe_allow_html=True)
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

# 📌 Anomaly Detection
elif option == "Anomaly Detection":
    st.subheader("🚨 Detect Anomalies in Data")
    if st.button("Check for Anomalies"):
        response = requests.get(f"{BACKEND_URL}/anomalies")
        anomalies = response.json().get("anomalies", [])
        st.write("🔍 Anomalies Found:")
        st.write(anomalies)
