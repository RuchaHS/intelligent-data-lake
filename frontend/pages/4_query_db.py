import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="Query DuckDB", layout="wide")
st.sidebar.title("🔎 Query DuckDB")

BACKEND_URL = "http://localhost:8000/db"

st.title("🔎 Run SQL Queries on DuckDB")

# ✅ Fetch available tables
tables_response = requests.get(f"{BACKEND_URL}/list-tables")

if tables_response.status_code == 200:
    tables = tables_response.json()["tables"]
    selected_table = st.selectbox("📌 Select a table to preview", ["(Choose a table)"] + tables)
    
    if selected_table != "(Choose a table)":
        preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
        if preview_response.status_code == 200:
            df_preview = pd.DataFrame(preview_response.json()["preview"])
            st.subheader("📋 Table Preview")
            st.dataframe(df_preview)
        else:
            st.error(preview_response.text)

# ✅ SQL Query Input
st.subheader("✍️ Write Your SQL Query")
query_text = st.text_area("Enter SQL query:", height=150)

if st.button("Run Query"):
    if query_text.strip():
        with st.spinner("🔄 Executing Query..."):
            response = requests.post(f"{BACKEND_URL}/run-query", data={"query_text": query_text})
        if response.status_code == 200:
            results = response.json().get("query_results", [])
            if results:
                df_results = pd.DataFrame(results)
                st.subheader("📊 Query Results")
                st.dataframe(df_results)

                # ✅ Provide Download Option
                csv = df_results.to_csv(index=False).encode("utf-8")
                json_data = json.dumps(results, indent=4)

                st.download_button("📥 Download as CSV", csv, "query_results.csv", "text/csv")
                st.download_button("📥 Download as JSON", json_data, "query_results.json", "application/json")

            else:
                st.info("✅ Query executed successfully, but no results found.")
        else:
            st.error(f"❌ Error: {response.text}")
    else:
        st.warning("⚠️ Please enter a valid SQL query.")
