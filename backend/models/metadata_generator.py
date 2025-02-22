import pandas as pd
import os

class MetadataGenerator:
    def __init__(self, model_name="mistral"):
        self.report_folder = "backend/reports"
        os.makedirs(self.report_folder, exist_ok=True)

    def generate_metadata(self, data_path):
        df = pd.read_csv(data_path)

        # ✅ Generate Dataprep Report
        report_filename = os.path.join(self.report_folder, f"{os.path.basename(data_path)}_dataprep_report.html")
        report = create_report(df)
        report.save(report_filename)

        return {
            "columns": df.columns.tolist(),
            "row_count": df.shape[0],
            "profiling_report": report_filename  # ✅ Return link to the report
        }
