from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import duckdb
import pandas as pd
import io
import json
import numpy as np
from sentence_transformers import SentenceTransformer  # ✅ For embeddings
from database import DB_PATH
from models.metadata_generator import MetadataGenerator
from models.anomaly_detector import AnomalyDetector
from models.data_quality_rules_generator import DataQualityGenerator
from models.query_optimizer import QueryOptimizer
from models.vector_search import VectorSearch

router = APIRouter(tags=["Database Processing"])

# ✅ Connect to DuckDB
conn = duckdb.connect(DB_PATH)

# ✅ Initialize Models
metadata_generator = MetadataGenerator()
anomaly_detector = AnomalyDetector()
data_quality_generator = DataQualityGenerator()
query_optimizer = QueryOptimizer()
vector_search = VectorSearch()

# ✅ Load Embedding Model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # ✅ Fast & efficient

# --------------------------------
# ✅ DATABASE OPERATIONS
# --------------------------------

def execute_query(query: str):
    """Executes a SQL query in DuckDB and returns results as DataFrame."""
    try:
        return conn.execute(query).fetchdf()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")

def insert_metadata(table_name, file_name, file_type):
    """Inserts metadata of uploaded files into DuckDB."""
    conn.execute("INSERT INTO file_metadata (table_name, file_name, file_type) VALUES (?, ?, ?)",
                 (table_name, file_name, file_type))

def read_file(file: UploadFile, file_type: str) -> pd.DataFrame:
    """Reads various file formats into a Pandas DataFrame."""
    try:
        if file_type == "csv":
            return pd.read_csv(io.StringIO(file.file.read().decode("utf-8")))
        elif file_type == "json":
            return pd.read_json(io.StringIO(file.file.read().decode("utf-8")))
        elif file_type == "parquet":
            return pd.read_parquet(io.BytesIO(file.file.read()))
        elif file_type in ["xls", "xlsx"]:
            return pd.read_excel(io.BytesIO(file.file.read()), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), table_name: str = Form(...)):
    """Uploads CSV, JSON, Parquet, or Excel file and stores in DuckDB."""
    try:
        file_ext = file.filename.split(".")[-1].lower()
        df = read_file(file, file_ext)

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # ✅ Convert column names to lowercase (avoid SQL conflicts)
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        # ✅ Store in DuckDB
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")

        # ✅ Insert into metadata table
        insert_metadata(table_name, file.filename, file_ext)

        return {"message": f"File `{file.filename}` uploaded to `{table_name}` successfully!", "columns": df.columns.tolist()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File Upload Error: {e}")

@router.get("/list-tables")
def list_tables():
    """Lists all tables in DuckDB."""
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        return {"tables": [t[0] for t in tables]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview-table/{table_name}")
def preview_table(table_name: str):
    """Fetches first 10 rows of a DuckDB table for preview."""
    try:
        df = execute_query(f"SELECT * FROM {table_name} LIMIT 10")
        return {"preview": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-query")
def run_query(query_text: str = Form(...)):
    """Executes a SQL query on DuckDB and returns results."""
    try:
        if "DROP" in query_text.upper() or "DELETE" in query_text.upper():
            raise HTTPException(status_code=400, detail="🚨 Dangerous query detected! Only SELECT statements are allowed.")

        df = execute_query(query_text)

        # ✅ Replace problematic float values for JSON compatibility
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna("null", inplace=True)  # Replace NaN with a string "null"

        return {"query_results": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")

def execute_query(query: str):
    """Executes SQL query in DuckDB and returns DataFrame."""
    try:
        return conn.execute(query).fetchdf()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")

# --------------------------------
# ✅ FEATURED ANALYSIS OPERATIONS
# --------------------------------

@router.get("/extract-metadata/{table_name}")
def extract_metadata(table_name: str):
    """Extracts metadata from a DuckDB table."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        metadata = metadata_generator.generate_metadata(df)
        return {"metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect-anomalies/{table_name}")
def detect_anomalies(table_name: str):
    """Detects anomalies in a DuckDB table."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        anomalies = anomaly_detector.detect_anomalies(df)
        return {"anomalies": anomalies.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-quality-rules/{table_name}")
def generate_quality_rules(table_name: str):
    """Generates data quality rules for a DuckDB table."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        rules = data_quality_generator.generate_quality_rules(df)
        return {"rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-query")
def optimize_query(query_text: str = Form(...)):
    """Optimizes SQL queries using AI-based query optimizer."""
    try:
        optimized_query = query_optimizer.optimize_query(query_text)
        return {"optimized_query": optimized_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-search/{table_name}")
def perform_vector_search(table_name: str, query: str):
    """Performs vector-based search using embeddings in DuckDB."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")

        # ✅ Generate embeddings for the search query
        query_embedding = embedder.encode(query).tolist()

        # ✅ Generate embeddings for each row & find similarity
        df["vector"] = df.apply(lambda row: embedder.encode(" ".join(row.astype(str))).tolist(), axis=1)
        df["similarity"] = df["vector"].apply(lambda vec: np.dot(vec, query_embedding) / (np.linalg.norm(vec) * np.linalg.norm(query_embedding)))

        # ✅ Sort by similarity & return top results
        results = df.sort_values(by="similarity", ascending=False).head(5).drop(columns=["vector", "similarity"])
        
        return {"results": results.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
