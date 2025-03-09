import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="Upload to DuckDB", layout="wide")
st.sidebar.title("📂 File Upload to DuckDB")

BACKEND_URL = "http://localhost:8000/db"

st.title("📂 Upload Files to DuckDB")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "json", "parquet", "xls", "xlsx"])
table_name = st.text_input("Enter table name:")

if uploaded_file and table_name:
    if st.button("Upload"):
        with st.spinner("🚀 Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/upload-file", files=files, data={"table_name": table_name})
        
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(response.text)

st.subheader("🔍 Existing Tables in DuckDB")
tables_response = requests.get(f"{BACKEND_URL}/list-tables")

if tables_response.status_code == 200:
    tables = tables_response.json()["tables"]
    selected_table = st.selectbox("Select a table to preview:", tables)
    
    if selected_table:
        preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
        if preview_response.status_code == 200:
            df_preview = pd.DataFrame(preview_response.json()["preview"])
            st.dataframe(df_preview)
        else:
            st.error(preview_response.text)
