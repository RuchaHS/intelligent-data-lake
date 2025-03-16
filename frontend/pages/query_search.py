import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000/db"

def run():
    st.title("🔎 Run Queries or Search Data")

    # ✅ SQL Query Box
    query_text = st.text_area("Enter SQL Query")
    if st.button("Run SQL Query"):
        response = requests.post(f"{BACKEND_URL}/run-query", data={"query_text": query_text})
        if response.status_code == 200:
            st.dataframe(pd.DataFrame(response.json()["query_results"]))
        else:
            st.error(response.text)

    # ✅ Vector Search
    search_query = st.text_input("Enter Search Query (for Vector Search)")
    if st.button("Search Vectors"):
        response = requests.get(f"{BACKEND_URL}/vector-search/{selected_table}", params={"query": search_query})
        if response.status_code == 200:
            st.json(response.json()["results"])
        else:
            st.error(response.text)