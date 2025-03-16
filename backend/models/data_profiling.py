import pandas as pd
import os
from ydata_profiling import ProfileReport  # ✅ Import ydata-profiling
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse  # ✅ Import FastAPI responses

class DataProfiler:
    """Generates data profiling reports in HTML and JSON formats using ydata-profiling"""

    def __init__(self):
        """Initialize the Data Profiler class with a report folder"""
        self.report_folder = "profiling_reports"
        os.makedirs(self.report_folder, exist_ok=True)  # ✅ Ensure report folder exists

    def generate_profile_report(self, df: pd.DataFrame, table_name: str) -> dict:
        """
        Generate a detailed profiling report using ydata-profiling.

        Args:
            df (pd.DataFrame): The input DataFrame for profiling.
            table_name (str): A unique name for the report file.

        Returns:
            dict: A dictionary with metadata information and report paths.
        """
        if df.empty:
            raise ValueError("Dataset is empty. Cannot generate profile report.")

        # ✅ Define report paths
        html_report_path = os.path.join(self.report_folder, f"{table_name}_profiling_report.html")
        json_report_path = os.path.join(self.report_folder, f"{table_name}_profiling_report.json")

        # ✅ Generate profiling report
        profile = ProfileReport(df, title=f"Data Profiling Report - {table_name}", explorative=True)
        profile.to_file(html_report_path)  # ✅ Save as HTML
        
        # ✅ Convert to JSON and save manually
        json_data = profile.to_json()
        with open(json_report_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_data)

        return {
            "columns": df.columns.tolist(),
            "row_count": df.shape[0],
            "html_report": html_report_path,
            "json_report": json_report_path
        }

    def get_html_report(self, table_name: str):
        """Fetches the saved HTML report file"""
        html_path = os.path.join(self.report_folder, f"{table_name}_profiling_report.html")
        if not os.path.exists(html_path):
            return JSONResponse(content={"error": "Profiling report not found"}, status_code=404)
        return FileResponse(html_path, media_type="text/html")

    def get_json_report(self, table_name: str):
        """Fetches the saved JSON report file"""
        json_path = os.path.join(self.report_folder, f"{table_name}_profiling_report.json")
        if not os.path.exists(json_path):
            return JSONResponse(content={"error": "Profiling report not found"}, status_code=404)
        return FileResponse(json_path, media_type="application/json")

    def render_html_report(self, table_name: str):
        """Returns HTML content for embedding inside an iframe"""
        html_path = os.path.join(self.report_folder, f"{table_name}_profiling_report.html")
        if not os.path.exists(html_path):
            return HTMLResponse(content="<h3>Profiling Report Not Found</h3>", status_code=404)

        with open(html_path, "r", encoding="utf-8") as file:
            report_html = file.read()

        return HTMLResponse(content=report_html, status_code=200)