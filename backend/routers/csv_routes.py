from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import pandas as pd
import os
import io
import json
from models.metadata_generator import MetadataGenerator
from models.anomaly_detector import AnomalyDetector
from models.data_quality_rules_generator import DataQualityGenerator
from models.query_optimizer import QueryOptimizer
from models.vector_search import VectorSearch

router = APIRouter(tags=["CSV Processing"])

# ✅ Data Storage Paths
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Initialize Models
metadata_generator = MetadataGenerator()
anomaly_detector = AnomalyDetector()
data_quality_generator = DataQualityGenerator()
query_optimizer = QueryOptimizer()
vector_search = VectorSearch()

def read_csv_file(file: UploadFile) -> pd.DataFrame:
    """Reads an uploaded CSV file into a Pandas DataFrame."""
    try:
        return pd.read_csv(io.StringIO(file.file.read().decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {e}")

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Uploads CSV file, reads it into a DataFrame, and stores it."""
    try:
        df = read_csv_file(file)
        return {"message": "File uploaded and read successfully", "columns": df.columns.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata")
async def extract_metadata(file: UploadFile = File(...)):
    """Extracts metadata from CSV."""
    try:
        df = read_csv_file(file)
        metadata = metadata_generator.generate_metadata(df)
        return {"metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-anomalies")
async def detect_anomalies(file: UploadFile = File(...)):
    """Detects anomalies in uploaded CSV data."""
    try:
        df = read_csv_file(file)
        anomalies_df = anomaly_detector.detect_anomalies(df)
        if anomalies_df.empty:
            return {"message": "No anomalies detected", "anomalies": []}
        return {"message": "Anomalies detected", "anomalies": json.loads(anomalies_df.to_json(orient="records"))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-quality-rules")
async def generate_quality_rules(file: UploadFile = File(...)):
    """Generates data quality rules from CSV."""
    try:
        df = read_csv_file(file)
        rules = data_quality_generator.generate_quality_rules(df)
        return {"message": "Data quality rules generated", "rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/optimize-query")
# async def optimize_query(query_text: str = Form(...)):
#     """Optimizes a SQL query using LLM (Ollama)."""
#     try:
#         response = ollama.chat(model="mistral", messages=[{"role": "user", "content": f"Optimize this SQL query: {query_text}"}])
#         return {"optimized_query": response["message"]["content"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector-search")
async def perform_vector_search(query: str = Form(...), file: UploadFile = File(...)):
    """Performs vector-based search on uploaded CSV."""
    try:
        df = read_csv_file(file)
        results = vector_search.search_vectors(df, query)
        return {"message": "Vector search completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
