import streamlit as st
import requests
import pandas as pd
import time

BACKEND_URL = "http://localhost:8000/db"

def run():
    st.title("📂 Upload Data to DuckDB")

    # ✅ Sidebar for Table Selection & Querying
    st.sidebar.subheader("📋 Existing Tables")
    
    tables_response = requests.get(f"{BACKEND_URL}/list-tables")
    if tables_response.status_code == 200:
        tables = tables_response.json()["tables"]
        selected_table = st.sidebar.radio("Select a table:", tables)

    # ✅ File Upload Section
    st.subheader("📂 Upload File")
    uploaded_file = st.file_uploader("Upload CSV, JSON, or Excel", type=["csv", "json", "xls", "xlsx"])
    table_name = st.text_input("Table Name (if storing in DuckDB)")

    # ✅ Checkbox for Auto Data Cleaning
    auto_clean = st.checkbox("Enable Auto Data Cleaning", value=True)

    if uploaded_file and table_name:
        if st.button("🚀 Upload & Store in DuckDB"):
            with st.spinner("Uploading and processing data..."):
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                response = requests.post(
                    f"{BACKEND_URL}/upload-file",
                    files=files,
                    data={"table_name": table_name, "auto_clean": str(auto_clean)}  # ✅ Send checkbox value
                )

            if response.status_code == 200:
                success_message = f"✅ File `{uploaded_file.name}` uploaded to `{table_name}` successfully! 🎉\n\n🔄 Table `{table_name}` is now available in the sidebar."

                # ✅ Add a message if Auto Data Cleaning is enabled
                if auto_clean:
                    success_message += "\n🛠 **Auto Data Cleaning Applied!** The table has been cleaned and stored."

                st.success(success_message)
                st.toast("🔄 Refreshing UI to update table list...")
                time.sleep(3)
                st.rerun()
            else:
                st.error(response.text)

    # ✅ Expandable Table Preview
    if selected_table:
        with st.expander(f"📋 Preview Data for `{selected_table}`"):
            preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
            if preview_response.status_code == 200:
                df_preview = pd.DataFrame(preview_response.json()["preview"])
                st.dataframe(df_preview)

if __name__ == "__main__":
    run()