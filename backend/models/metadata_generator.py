import pandas as pd
import sweetviz as sv
import os

class MetadataGenerator:
    def __init__(self):
        self.report_folder = os.path.abspath("backend/profiling_reports")
        os.makedirs(self.report_folder, exist_ok=True)

    def generate_metadata(self, data_path):
        df = pd.read_csv(data_path)

        # ✅ Generate Sweetviz Report
        report_filename = os.path.join(self.report_folder, f"{os.path.splitext(os.path.basename(data_path))[0]}_sweetviz_report.html")
        report = sv.analyze(df)
        report.show_html(report_filename, open_browser=False)

        return {
            "columns": df.columns.tolist(),
            "row_count": df.shape[0],
            "profiling_report": report_filename
        }
