import pandas as pd
import numpy as np
import plotly.express as px
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

    def detect_anomalies(self, df: pd.DataFrame) -> tuple:
        """Detect anomalies using a hybrid ensemble of PyOD models and explain them visually."""
        if df.empty:
            raise ValueError("Dataset is empty")

        # ✅ Select only numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset")

        # ✅ Handle missing values
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

        # ✅ Generate a basic explanation
        anomaly_count = anomalies.shape[0]
        total_count = df.shape[0]
        percentage_anomalies = (anomaly_count / total_count) * 100

        explanation = {
            "total_records": total_count,
            "anomalies_detected": anomaly_count,
            "anomaly_percentage": round(percentage_anomalies, 2),
            "message": f"Detected {anomaly_count} anomalies out of {total_count} records, which is {round(percentage_anomalies, 2)}% of the dataset."
        }

        # ✅ Generate a scatter plot using plotly (choose first numeric column for visualization)
        first_numeric_col = numeric_df.columns[0] if not numeric_df.empty else None
        fig_json = None
        if first_numeric_col:
            fig = px.scatter(anomalies_df, x=first_numeric_col, y=first_numeric_col, color="Anomaly",
                            title=f"Anomaly Detection: {first_numeric_col}",
                            labels={"Anomaly": "Anomaly Status"})
            fig_json = fig.to_json()

        return anomalies, explanation, fig_json  # ✅ Now returns a tuple