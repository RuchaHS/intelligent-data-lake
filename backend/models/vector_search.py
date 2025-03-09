import faiss
import numpy as np
import pandas as pd
import duckdb
from transformers import AutoTokenizer, AutoModel

class VectorSearch:
    def __init__(self):
        # ✅ Load Pretrained Sentence Embedding Model
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # ✅ FAISS Index for Efficient Search
        self.index = faiss.IndexFlatL2(384)  # 384 = embedding dimension
        self.metadata = []  # Stores metadata for lookup

    def embed_text(self, text):
        """ Converts text into vector embedding using Transformer model. """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()

    def build_index_from_csv(self, file_path):
        """ Builds FAISS index from uploaded CSV data. """
        df = pd.read_csv(file_path)
        self.metadata = df.columns.tolist()  # Store column names as metadata
        embeddings = np.array([self.embed_text(col) for col in self.metadata])
        
        # ✅ Update FAISS Index
        self.index.reset()  # Clear existing index
        self.index.add(embeddings)
        return {"message": "FAISS index built from CSV", "columns": self.metadata}

    def build_index_from_duckdb(self, db_path, table_name):
        """ Builds FAISS index from DuckDB table schema. """
        conn = duckdb.connect(db_path)
        query = f"DESCRIBE {table_name}"
        df = conn.execute(query).fetchdf()
        
        self.metadata = df["column_name"].tolist()  # Extract column names
        embeddings = np.array([self.embed_text(col) for col in self.metadata])
        
        # ✅ Update FAISS Index
        self.index.reset()  # Clear existing index
        self.index.add(embeddings)
        return {"message": "FAISS index built from DuckDB", "columns": self.metadata}

    def search(self, query, k=3):
        """ Searches for the closest column names based on query embedding. """
        if not self.metadata:
            return {"error": "Index not built yet. Please build an index first."}
        
        query_embedding = self.embed_text(query)
        _, indices = self.index.search(query_embedding, k)
        return [self.metadata[i] for i in indices[0]]
