import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ✅ FastAPI Backend URL
BACKEND_URL = "http://localhost:8000/db"

# ✅ Configure Page
st.set_page_config(page_title="📊 Data Visualization", layout="wide")
st.sidebar.title("📈 Data Visualization")

# 🔹 Load available tables
@st.cache_data
def get_tables():
    response = requests.get(f"{BACKEND_URL}/list-tables")
    if response.status_code == 200:
        return response.json()["tables"]
    return []

tables = get_tables()

# ✅ Step 1: Select Table
st.sidebar.subheader("📌 Select Table")
selected_table = st.sidebar.selectbox("Choose a table:", ["(Choose a table)"] + tables)

if selected_table and selected_table != "(Choose a table)":
    # 🔹 Load data from selected table
    @st.cache_data
    def load_data(table_name):
        response = requests.get(f"{BACKEND_URL}/preview-table/{table_name}")
        if response.status_code == 200:
            return pd.DataFrame(response.json()["preview"])
        return pd.DataFrame()

    df = load_data(selected_table)
    if df.empty:
        st.warning("⚠️ No data found in the selected table.")
    else:
        st.dataframe(df)  # Show preview

        # ✅ Step 2: Select Chart Type
        st.sidebar.subheader("📌 Select Chart Type")
        chart_type = st.sidebar.selectbox("Choose visualization type:", [
            "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart",
            "Histogram", "Box Plot", "Heatmap"
        ])

        # ✅ Step 3: Select Columns for Visualization
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = df.select_dtypes(exclude=["number"]).columns.tolist()

        x_axis = None
        y_axis = None

        if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"]:
            x_axis = st.sidebar.selectbox("Select X-axis:", df.columns)
            y_axis = st.sidebar.selectbox("Select Y-axis:", numeric_columns)

        elif chart_type == "Pie Chart":
            x_axis = st.sidebar.selectbox("Select Category Column:", categorical_columns)

        elif chart_type in ["Histogram", "Box Plot"]:
            x_axis = st.sidebar.selectbox("Select Numeric Column:", numeric_columns)

        elif chart_type == "Heatmap":
            if len(numeric_columns) < 2:
                st.warning("⚠️ Heatmap requires at least 2 numeric columns.")
                st.stop()
            heatmap_columns = st.sidebar.multiselect("Select Columns for Heatmap:", numeric_columns, default=numeric_columns[:2])

        # ✅ Step 4: Plot the Chart
        st.subheader(f"📊 {chart_type} Visualization")

        fig = None  # Initialize figure

        if chart_type == "Bar Chart":
            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")

        elif chart_type == "Line Chart":
            fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} Over {x_axis}")

        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")

        elif chart_type == "Pie Chart":
            fig = px.pie(df, names=x_axis, title=f"Distribution of {x_axis}")

        elif chart_type == "Histogram":
            fig = px.histogram(df, x=x_axis, title=f"Histogram of {x_axis}")

        elif chart_type == "Box Plot":
            fig = px.box(df, x=x_axis, title=f"Box Plot of {x_axis}")

        elif chart_type == "Heatmap":
            heatmap_data = df[heatmap_columns].corr()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
            st.pyplot(fig)

        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # ✅ Step 5: Download Options
        st.sidebar.subheader("📥 Download Report")

        # Convert Data to CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(label="📥 Download CSV", data=csv_data, file_name=f"{selected_table}_data.csv", mime="text/csv")

        # Convert Plot to Image
        img_buffer = io.BytesIO()
        fig.write_image(img_buffer, format="png") if fig else None
        st.sidebar.download_button(label="📷 Download Chart (PNG)", data=img_buffer, file_name=f"{chart_type}.png", mime="image/png")

        # Convert to PDF
        import pdfkit
        pdf_buffer = io.BytesIO()
        pdfkit.from_string(st.get_report_ctx().enqueue_text, pdf_buffer)
        st.sidebar.download_button(label="📄 Download Report (PDF)", data=pdf_buffer, file_name=f"{chart_type}_report.pdf", mime="application/pdf")

        # ✅ Step 6: User Customization
        with st.expander("⚙️ Customize Graph"):
            col1, col2 = st.columns(2)
            chart_height = col1.slider("Adjust Chart Height", 300, 800, 500)
            chart_width = col2.slider("Adjust Chart Width", 300, 1200, 800)
            fig.update_layout(height=chart_height, width=chart_width) if fig else None
            st.plotly_chart(fig, use_container_width=False) if fig else None

        st.success("✅ Visualization Complete!")
