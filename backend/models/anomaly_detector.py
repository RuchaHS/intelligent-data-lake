import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)

    def detect_anomalies(self, data_path):
        df = pd.read_csv(data_path)
        df["anomaly_score"] = self.model.fit_predict(df.select_dtypes(include=['number']))
        return df[df["anomaly_score"] == -1]  # Return anomalies
