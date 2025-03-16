import duckdb
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorSearch:
    def __init__(self, db_path="intelligent_data_lake.duckdb"):
        self.conn = duckdb.connect(db_path)
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def search_vectors(self, table_name, query):
        df = self.conn.execute(f"SELECT * FROM {table_name}").fetchdf()

        if df.empty:
            return {"message": "Table is empty", "results": []}

        query_embedding = self.embedder.encode(query).tolist()
        df["vector"] = df.apply(lambda row: self.embedder.encode(" ".join(row.astype(str))).tolist(), axis=1)
        df["similarity"] = df["vector"].apply(lambda vec: np.dot(vec, query_embedding) / (np.linalg.norm(vec) * np.linalg.norm(query_embedding)))

        results = df.sort_values(by="similarity", ascending=False).head(5).drop(columns=["vector", "similarity"])
        return {"message": "Vector search completed", "results": results.to_dict(orient="records")}