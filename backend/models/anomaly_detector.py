import pandas as pd
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.hbos import HBOS
from pyod.models.cblof import CBLOF
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self):
        """Initialize multiple models for hybrid anomaly detection."""
        self.models = {
            "iforest": IForest(contamination=0.02, random_state=42),
            "hbos": HBOS(contamination=0.02),
            "cblof": CBLOF(contamination=0.02, random_state=42),
            "knn": KNN(contamination=0.02),
            "lof": LOF(contamination=0.02)
        }

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using a hybrid ensemble of PyOD models."""
        if df.empty:
            raise ValueError("Dataset is empty")

        # ✅ Select only numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset")

        # ✅ Check and handle missing values
        if numeric_df.isnull().values.any():
            print(f"⚠️ Warning: Found {numeric_df.isnull().sum().sum()} missing values. Imputing with median.")
            numeric_df = numeric_df.fillna(numeric_df.median())  # ✅ Replace NaN with median

        # ✅ Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)

        # ✅ Fit and predict using all models
        predictions = []
        for name, model in self.models.items():
            model.fit(scaled_data)
            predictions.append(model.predict(scaled_data))

        # ✅ Aggregate predictions (majority voting)
        final_anomalies = np.mean(predictions, axis=0) >= 0.4  # Mark as anomaly if at least 2 models agree
        final_anomalies = final_anomalies.astype(int)

        # ✅ Append anomaly labels
        anomalies_df = df.copy()
        anomalies_df["Anomaly"] = final_anomalies

        # ✅ Extract only anomalies
        anomalies = anomalies_df[anomalies_df["Anomaly"] == 1].copy()

        # ✅ Handle infinite values for JSON compliance
        anomalies.replace([np.inf, -np.inf], np.nan, inplace=True)
        anomalies.fillna(0, inplace=True)

        return anomalies  # ✅ Return DataFrame with detected anomalies
