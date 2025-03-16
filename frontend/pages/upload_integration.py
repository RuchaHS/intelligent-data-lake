import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000/db"

def run():
    st.title("📂 Upload Data or Connect to DuckDB")

    uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    table_name = st.text_input("Table Name (if storing in DuckDB)")

    if uploaded_file and table_name:
        if st.button("🚀 Upload & Store in DuckDB"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/upload-file", files=files, data={"table_name": table_name})

            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.text)

    # 🔹 Show existing tables
    tables_response = requests.get(f"{BACKEND_URL}/list-tables")
    if tables_response.status_code == 200:
        tables = tables_response.json()["tables"]
        selected_table = st.selectbox("📋 Select a table to preview:", ["(Choose a table)"] + tables)
        
        if selected_table and selected_table != "(Choose a table)":
            preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
            if preview_response.status_code == 200:
                df_preview = pd.DataFrame(preview_response.json()["preview"])
                st.dataframe(df_preview)