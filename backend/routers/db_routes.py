from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import duckdb
import pandas as pd
import io
import numpy as np
from fastapi.responses import FileResponse
from sentence_transformers import SentenceTransformer
from models.data_profiling import DataProfiler
from database import DB_PATH
from models.metadata_generator import MetadataGenerator
from models.anomaly_detector import AnomalyDetector
from models.data_quality_rules_generator import DataQualityGenerator
from models.query_optimizer import QueryOptimizer
from models.vector_search import VectorSearch

router = APIRouter(prefix="/db", tags=["Database Processing"])

# ✅ Connect to DuckDB
conn = duckdb.connect(DB_PATH)

# ✅ Initialize Models
metadata_generator = MetadataGenerator()
anomaly_detector = AnomalyDetector()
data_quality_generator = DataQualityGenerator()
query_optimizer = QueryOptimizer()
vector_search = VectorSearch()
data_profiler = DataProfiler()

# ✅ Load Embedding Model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --------------------------------
# ✅ DATABASE OPERATIONS
# --------------------------------

def execute_query(query: str):
    """Executes SQL query in DuckDB and returns results as a Pandas DataFrame."""
    try:
        return conn.execute(query).fetchdf()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), table_name: str = Form(...)):
    """Uploads CSV, JSON, Parquet, or Excel file into DuckDB and saves embeddings."""
    try:
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext == "csv":
            df = pd.read_csv(io.StringIO(file.file.read().decode("utf-8")))
        elif file_ext == "json":
            df = pd.read_json(io.StringIO(file.file.read().decode("utf-8")))
        elif file_ext == "parquet":
            df = pd.read_parquet(io.BytesIO(file.file.read()))
        elif file_ext in ["xls", "xlsx"]:
            df = pd.read_excel(io.BytesIO(file.file.read()), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")

        # ✅ Generate & Store Embeddings
        df["vector"] = df.apply(lambda row: embedder.encode(" ".join(row.astype(str))).tolist(), axis=1)
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN vector ARRAY(float)")
        conn.executemany(f"UPDATE {table_name} SET vector = ? WHERE rowid = ?", list(zip(df["vector"], range(1, len(df) + 1))))

        return {"message": f"File `{file.filename}` uploaded to `{table_name}` successfully!", "columns": df.columns.tolist()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File Upload Error: {e}")

@router.get("/list-tables")
def list_tables():
    """Lists all tables in DuckDB."""
    try:
        tables = conn.execute("SHOW TABLES").fetchdf()["name"].tolist()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview-table/{table_name}")
def preview_table(table_name: str):
    """Fetches first 10 rows of a DuckDB table for preview."""
    try:
        df = execute_query(f"SELECT * FROM {table_name} LIMIT 20")
        return {"preview": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-query")
def run_query(query_text: str = Form(...)):
    """Executes a SQL query on DuckDB."""
    try:
        if any(keyword in query_text.upper() for keyword in ["DROP", "DELETE", "ALTER"]):
            raise HTTPException(status_code=400, detail="🚨 Dangerous query detected! Only SELECT statements are allowed.")

        df = execute_query(query_text)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna("null", inplace=True)

        return {"query_results": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")

@router.get("/table-schema/{table_name}")
def get_table_schema(table_name: str):
    """Returns column names and data types for a given table in DuckDB."""
    try:
        schema = execute_query(f"PRAGMA table_info({table_name})")
        return {"schema": schema.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {e}")

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

        if anomalies.empty:
            return {"message": "No anomalies detected.", "anomalies": []}

        return {"message": "Anomaly detection completed.", "anomalies": anomalies.to_dict(orient="records")}

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

# --------------------------------
# ✅ data Profiling
# --------------------------------
@router.get("/profile-data/{table_name}")
def profile_data(table_name: str):
    """Generates a data profiling report for a DuckDB table."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")

        if df.empty:
            return {"message": "Table is empty", "profiling_report": None}

        profiling_result = data_profiler.generate_profile_report(df, table_name)
        return profiling_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-profile-report/{table_name}/{format}")
def download_profile_report(table_name: str, format: str):
    """Allows users to download the data profiling report in HTML or JSON."""
    try:
        if format == "html":
            return data_profiler.get_html_report(table_name)
        elif format == "json":
            return data_profiler.get_json_report(table_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Choose 'html' or 'json'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view-profile-report/{table_name}")
def view_profile_report(table_name: str):
    """Embeds the profiling report inside an iframe for visualization."""
    return data_profiler.render_html_report(table_name)


@router.get("/vector-search/{table_name}")
def perform_vector_search(table_name: str, query: str):
    """Performs vector-based search using embeddings in DuckDB."""
    try:
        df = execute_query(f"SELECT * FROM {table_name}")

        if df.empty:
            return {"message": "Table is empty", "results": []}

        query_embedding = embedder.encode(query).tolist()

        df["vector"] = df.apply(lambda row: embedder.encode(" ".join(row.astype(str))).tolist(), axis=1)
        df["similarity"] = df["vector"].apply(lambda vec: np.dot(vec, query_embedding) / (np.linalg.norm(vec) * np.linalg.norm(query_embedding)))

        results = df.sort_values(by="similarity", ascending=False).head(5).drop(columns=["vector", "similarity"])

        return {"message": "Vector search completed", "results": results.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))