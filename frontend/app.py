import streamlit as st
import importlib

# ✅ Set Streamlit Page Config
st.set_page_config(page_title="📊 Intelligent Data Lake", layout="wide")

# ✅ Sidebar Navigation
st.sidebar.title("📌 Navigation")

PAGES = {
    "🔗 DB Integration": "custom_pages.upload_integration",
    "📄 Query Database": "custom_pages.query_search",
    "🔤 Text-to-SQL & SQL-to-Text": "custom_pages.text_to_sql",
    "📊 Data Insights & Analysis": "custom_pages.analysis_insights",
    "📈 Data Visualization": "custom_pages.data_visualizations",
}

# ✅ User selects a page
selected_page = st.sidebar.radio("Select a page:", list(PAGES.keys()))  # Default selection

# ✅ Dynamically Import & Execute the Selected Page
module_name = PAGES[selected_page]
module = importlib.import_module(module_name)
module.run()