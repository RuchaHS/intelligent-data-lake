import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000/db"

def run():
    st.title("🔎 Run SQL Queries on DuckDB")

    tables_response = requests.get(f"{BACKEND_URL}/list-tables")

    if tables_response.status_code == 200:
        tables = tables_response.json()["tables"]
        selected_table = st.selectbox("📌 Select a table:", ["(Choose a table)"] + tables)

        if selected_table != "(Choose a table)":
            st.subheader(f"📋 Table Preview: `{selected_table}`")
            preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
            if preview_response.status_code == 200:
                df_preview = pd.DataFrame(preview_response.json()["preview"])
                st.dataframe(df_preview)

    query_text = st.text_area("✍️ Enter SQL query:", height=150)

    if st.button("Run Query"):
        if query_text.strip():
            response = requests.post(f"{BACKEND_URL}/run-query", data={"query_text": query_text})
            if response.status_code == 200:
                results = response.json()["query_results"]
                st.dataframe(pd.DataFrame(results))
            else:
                st.error(response.text)
        else:
            st.warning("⚠️ Please enter a valid SQL query.")