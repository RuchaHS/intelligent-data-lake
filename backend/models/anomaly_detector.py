import pandas as pd
import numpy as np
import io
from pycaret.anomaly import setup, create_model, assign_model

class AnomalyDetector:
    def __init__(self):
        self.model = None

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in a dataset and return a DataFrame."""
        if df.empty:
            raise ValueError("Dataset is empty")

        # ✅ Select only numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset")

        # ✅ PyCaret Setup
        setup(data=numeric_df, session_id=123, verbose=False)
        self.model = create_model("iforest")  # ✅ Isolation Forest
        anomalies_df = assign_model(self.model)

        if "Anomaly" not in anomalies_df.columns:
            raise ValueError("Anomaly column missing from PyCaret output")

        # ✅ Extract only anomalous rows
        anomalies = anomalies_df[anomalies_df["Anomaly"] == 1].copy()
        
        if anomalies.empty:
            return pd.DataFrame()  # ✅ Return an empty DataFrame if no anomalies are found

        # ✅ Ensure JSON compliance (convert non-serializable values)
        anomalies.replace([np.inf, -np.inf], np.nan, inplace=True)
        anomalies.fillna(0, inplace=True)

        return anomalies  # ✅ Directly return DataFrame
