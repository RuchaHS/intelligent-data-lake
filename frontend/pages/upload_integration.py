import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000/db"

def run():
    # ✅ Set SQL Server-like UI
    st.set_page_config(page_title="SQL Database Manager", layout="wide")

    # 🎯 **Sidebar - Table List**
    st.sidebar.title("📂 Database Tables")

    # Fetch table list
    tables_response = requests.get(f"{BACKEND_URL}/list-tables")
    tables = tables_response.json()["tables"] if tables_response.status_code == 200 else []

    selected_table = st.sidebar.radio("📌 Select a table", ["(Choose a table)"] + tables)

    # ✅ **Main UI - Data Upload Section**
    st.title("📂 Upload Data or Connect to DuckDB")
    uploaded_file = st.file_uploader("📤 Upload CSV or JSON", type=["csv", "json"])
    table_name = st.text_input("📝 Table Name (if storing in DuckDB)")

    if uploaded_file and table_name:
        if st.button("🚀 Upload & Store in DuckDB"):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/upload-file", files=files, data={"table_name": table_name})

            if response.status_code == 200:
                st.success(response.json()["message"])
                st.rerun()  # ✅ Refresh UI to show the new table
            else:
                st.error(response.text)

    # ✅ **Show Preview When Table is Selected**
    if selected_table and selected_table != "(Choose a table)":
        st.subheader(f"📊 Preview Table : `{selected_table}`")
        preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
        
        if preview_response.status_code == 200:
            df_preview = pd.DataFrame(preview_response.json()["preview"])
            df_preview.fillna("N/A", inplace=True)  # ✅ Fix missing values
            st.dataframe(df_preview, height=400)

if __name__ == "__main__":
    run()