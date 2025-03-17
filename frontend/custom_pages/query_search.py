import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000/db"

def run():
    st.title("🔎 Run Queries or Search Data")

    # ✅ Sidebar Navigation
    st.sidebar.header("📌 Database Operations")

    # ✅ Fetch and List Tables in Sidebar
    tables_response = requests.get(f"{BACKEND_URL}/list-tables")
    selected_table = None

    if tables_response.status_code == 200:
        tables = tables_response.json()["tables"]
        selected_table = st.sidebar.selectbox("📋 Select a table:", ["(Choose a table)"] + tables)

    if selected_table != "(Choose a table)":
        st.subheader(f"📋 Table Preview: `{selected_table}`")
        preview_response = requests.get(f"{BACKEND_URL}/preview-table/{selected_table}")
        
        if preview_response.status_code == 200:
            df_preview = pd.DataFrame(preview_response.json()["preview"])
            df_preview.fillna("N/A", inplace=True)  # ✅ Fix: Replace null values for proper rendering
            st.dataframe(df_preview)

    # ✅ SQL Query Box in Main Page
    st.subheader("📝 SQL Query")
    query_text = st.text_area("Enter SQL Query")
    if st.button("Run SQL Query"):
        response = requests.post(f"{BACKEND_URL}/run-query", data={"query_text": query_text})
        if response.status_code == 200:
            st.subheader("📝 Query Results")
            st.dataframe(pd.DataFrame(response.json()["query_results"]))
        else:
            st.error(response.text)

    # # ✅ Vector Search in Main Page
    # st.subheader("🔍 Vector Search")
    # search_query = st.text_input("Enter Vector Search Query")
    # if st.button("Search Vectors"):
    #     response = requests.get(f"{BACKEND_URL}/vector-search/{selected_table}", params={"query": search_query})
    #     if response.status_code == 200:
    #         st.subheader("🔍 Vector Search Results")
    #         st.json(response.json()["results"])
    #     else:
    #         st.error(response.text)
