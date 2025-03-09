import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.hbos import HBOS
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self):
        """Initialize both models for hybrid anomaly detection."""
        self.iforest = IForest(contamination=0.02, random_state=42)  # ✅ Isolation Forest
        self.hbos = HBOS(contamination=0.02)  # ✅ HBOS (super fast)

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using hybrid Isolation Forest + HBOS."""
        if df.empty:
            raise ValueError("Dataset is empty")

        # ✅ Select only numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset")

        # ✅ Check Missing Values Before Processing
        if numeric_df.isnull().values.any():
            print(f"⚠️ Warning: Found {numeric_df.isnull().sum().sum()} missing values. Imputing with median.")
            numeric_df = numeric_df.fillna(numeric_df.median())  # ✅ Replace NaN with median

        # ✅ Standardize Data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)

        # ✅ Fit Both Models
        self.iforest.fit(scaled_data)
        self.hbos.fit(scaled_data)

        # ✅ Predict Anomalies
        iforest_preds = self.iforest.predict(scaled_data)
        hbos_preds = self.hbos.predict(scaled_data)

        # ✅ Combine Predictions (Anomalous if detected by either model)
        final_anomalies = np.logical_or(iforest_preds, hbos_preds).astype(int)

        # ✅ Append Anomaly Labels
        anomalies_df = df.copy()
        anomalies_df["Anomaly"] = final_anomalies

        # ✅ Extract Only Anomalies
        anomalies = anomalies_df[anomalies_df["Anomaly"] == 1].copy()

        # ✅ Handle Infinite Values for JSON Compliance
        anomalies.replace([np.inf, -np.inf], np.nan, inplace=True)
        anomalies.fillna(0, inplace=True)

        return anomalies  # ✅ Return the DataFrame with anomalies
