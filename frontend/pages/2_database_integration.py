import streamlit as st
import requests

st.title("📡 Database Integration (DuckDB)")

# ✅ Backend API URL
BACKEND_URL = "http://localhost:8000/db"

# ✅ Select Operation
operation = st.selectbox("Choose operation:", [
    "Text-to-SQL",
    "Extract Metadata",
    "Anomaly Detection",
    "Data Profiling",
    "Generate Data Quality Rules",
    "Optimize Query",
    "Vector Search"
])

# ✅ Text-to-SQL Query Execution
if operation == "Text-to-SQL":
    query_text = st.text_area("Enter Natural Language Query:")
    if st.button("Generate SQL & Execute"):
        response = requests.post(f"{BACKEND_URL}/text-to-sql", json={"query_text": query_text})
        if response.status_code == 200:
            data = response.json()
            st.code(data["sql_query"], language="sql")
            st.table(data["results"])
        else:
            st.error(response.text)

# ✅ Metadata Extraction
elif operation == "Extract Metadata":
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
                st.subheader("🚨 Detected Anomalies")
                st.dataframe(anomalies)
            else:
                st.success("✅ No anomalies detected.")
        else:
            st.error(response.text)

# ✅ Data Profiling
elif operation == "Data Profiling":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Generate Profiling Report"):
        response = requests.get(f"{BACKEND_URL}/profile-data-db", params={"table_name": table_name})
        if response.status_code == 200:
            report_url = response.json().get("profiling_report")
            if report_url:
                st.markdown(f"### 📊 [View Profiling Report]({BACKEND_URL}{report_url})", unsafe_allow_html=True)
            else:
                st.error("❌ Profiling report not generated.")
        else:
            st.error(response.text)

# ✅ Data Quality Rules Generation
elif operation == "Generate Data Quality Rules":
    table_name = st.text_input("Enter Table Name:")
    if st.button("Generate Rules"):
        response = requests.get(f"{BACKEND_URL}/data-quality-rules/{table_name}")
        if response.status_code == 200:
            rules = response.json().get("rules", {})
            st.json(rules)
        else:
            st.error(response.text)

# ✅ Query Optimization
elif operation == "Optimize Query":
    query_text = st.text_area("Enter SQL Query:")
    if st.button("Optimize Query"):
        response = requests.post(f"{BACKEND_URL}/optimize-query", json={"query_text": query_text})
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(response.text)

# ✅ Vector Search
# elif operation == "Vector Search":
#     table_name = st.text_input("Enter Table Name:")
#     query = st.text_input("Enter Search Query:")
#     if st.button("Perform Vector Search"):
#         response = requests.get(f"{BACKEND_URL}/vector-search/{table_name}", params={"query": query})
#         if response.status_code == 200:
#             st.json(response.json())
#         else:
#             st.error(response.text)
