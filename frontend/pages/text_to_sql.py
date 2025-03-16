import streamlit as st
import requests

# ✅ FastAPI Backend URL
BACKEND_URL = "http://localhost:8000/db"

def run():
    """Page for Text-to-SQL and SQL-to-Text translation."""
    st.title("📝 Text-to-SQL & SQL Explanation")

    # 🔹 Select Translation Type
    translation_type = st.radio("Choose an option:", ["Text-to-SQL", "SQL Explanation"])

    # ✅ Natural Language to SQL
    if translation_type == "Text-to-SQL":
        query_text = st.text_area("💬 Enter your natural language query:")
        
        if st.button("🔄 Convert to SQL"):
            with st.spinner("Generating SQL Query..."):
                response = requests.post(f"{BACKEND_URL}/text-to-sql", json={"query_text": query_text})
            
            if response.status_code == 200:
                sql_query = response.json().get("sql_query", "No SQL generated.")
                st.code(sql_query, language="sql")
            else:
                st.error(response.text)

    # ✅ SQL to Natural Language Explanation
    elif translation_type == "SQL Explanation":
        sql_query = st.text_area("🗄 Enter your SQL query:")
        
        if st.button("🔍 Explain SQL"):
            with st.spinner("Explaining SQL Query..."):
                response = requests.post(f"{BACKEND_URL}/sql-to-text", json={"query_text": sql_query})
            
            if response.status_code == 200:
                explanation = response.json().get("explanation", "No explanation generated.")
                st.write(explanation)
            else:
                st.error(response.text)

if __name__ == "__main__":
    run()