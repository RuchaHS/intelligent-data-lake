import streamlit as st
from pages import upload_integration, analysis_insights, query_search, data_visualizations, text_to_sql

# ✅ Configure Streamlit Page
# st.set_page_config(page_title="Intelligent Data Lake", layout="wide")

# ✅ Sidebar Navigation
st.sidebar.title("📊 Intelligent Data Lake")

# ✅ Define Tabs for Navigation
tabs = {
    "📂 Upload & Integration": upload_integration.run,
    "📊 Analysis & Insights": analysis_insights.run,
    "🔎 Query & Search": query_search.run,
    "📊 Data Visualization": data_visualizations.run,
    "📝 Text-to-SQL" : text_to_sql.run
}

# ✅ Display Tabs in Sidebar
selected_page = st.sidebar.radio("🔍 Select an operation:", list(tabs.keys()))

# ✅ Run the selected page
tabs[selected_page]()