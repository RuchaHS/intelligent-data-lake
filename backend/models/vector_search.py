import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
import pandas as pd

class VectorSearch:
    def __init__(self):
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.index = faiss.IndexFlatL2(384)  # 384 is embedding dimension

        self.metadata, self.embeddings = self.build_index("../data/data_science_job.csv")

    def embed_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()

    def build_index(self, data_path):
        df = pd.read_csv(data_path)
        metadata = df.columns.tolist()
        embeddings = np.array([self.embed_text(col) for col in metadata])

        self.index.add(embeddings)
        return metadata, embeddings

    def search(self, query):
        query_embedding = self.embed_text(query)
        _, indices = self.index.search(query_embedding, k=3)
        return [self.metadata[i] for i in indices[0]]
