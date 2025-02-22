# We will use KMeans clustering to automatically categorize datasets.

import pandas as pd
from sklearn.cluster import KMeans

class DataCategorizer:
    def __init__(self):
        self.model = KMeans(n_clusters=3)

    def categorize_data(self, data_path):
        df = pd.read_csv(data_path)
        df["category"] = self.model.fit_predict(df.select_dtypes(include=['number']))
        return df

if __name__ == "__main__":
    categorizer = DataCategorizer()
    categorized_data = categorizer.categorize_data("../data/data_science_job.csv")
    print(categorized_data)
