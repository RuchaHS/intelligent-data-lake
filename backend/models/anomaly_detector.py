import pandas as pd
from pycaret.anomaly import setup, create_model, assign_model

class AnomalyDetector:
    def __init__(self):
        self.model = None  # Model will be initialized in setup

    def detect_anomalies(self, data_path):
        df = pd.read_csv(data_path)

        # ✅ Ensure data contains only numeric features
        numeric_df = df.select_dtypes(include=["number"])

        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset for anomaly detection.")

        # ✅ PyCaret Setup & Model Creation
        setup(data=numeric_df, session_id=123, verbose=False)
        self.model = create_model("iforest")
        anomalies_df = assign_model(self.model)

        # ✅ Filter for detected anomalies
        anomalies = anomalies_df[anomalies_df["Anomaly_Score"] == 1].copy()

        return anomalies  # ✅ Return a DataFrame, NOT a list
