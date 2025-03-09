from fastapi import APIRouter, HTTPException
import duckdb
import pandas as pd
from models.query_optimizer import QueryOptimizer
from models.metadata_generator import MetadataGenerator
from models.anomaly_detector import AnomalyDetector
from models.data_quality_rules_generator import DataQualityGenerator
from models.vector_search import VectorSearch

router = APIRouter(tags=["Database Processing"])

# ✅ Connect to DuckDB
DB_PATH = "intelligent_data_lake.duckdb"
conn = duckdb.connect(DB_PATH)

# ✅ Initialize Models
query_optimizer = QueryOptimizer()
metadata_generator = MetadataGenerator()
anomaly_detector = AnomalyDetector()
data_quality_generator = DataQualityGenerator()
vector_search = VectorSearch()


def execute_query(query: str):
    """ Executes a SQL query in DuckDB and returns results as DataFrame. """
    try:
        return conn.execute(query).fetchdf()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Text-to-SQL Execution
@router.post("/text-to-sql")
def text_to_sql(query_text: str):
    try:
        sql_query = query_optimizer.text_to_sql(query_text)
        result = execute_query(sql_query)
        return {"sql_query": sql_query, "results": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Extract Metadata from DuckDB Tables
@router.get("/extract-metadata/{table_name}")
def extract_metadata(table_name: str):
    try:
        query = f"DESCRIBE {table_name}"
        metadata = execute_query(query).to_dict(orient="records")
        return {"metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Anomaly Detection in DuckDB Tables
@router.get("/detect-anomalies/{table_name}")
def detect_anomalies(table_name: str):
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        anomalies = anomaly_detector.detect_anomalies(df)
        return {"message": "Anomaly detection completed", "anomalies": anomalies.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Generate Data Quality Rules from DuckDB
@router.get("/data-quality-rules/{table_name}")
def generate_quality_rules(table_name: str):
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        rules = data_quality_generator.generate_quality_rules(df)
        return {"message": "Data quality rules generated", "rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Optimize Queries using AI
@router.post("/optimize-query")
def optimize_query(query_text: str):
    try:
        optimized_query = query_optimizer.optimize_query(query_text)
        return {"optimized_query": optimized_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Vector Search in DuckDB Tables
@router.get("/vector-search/{table_name}")
def perform_vector_search(table_name: str, query: str):
    try:
        df = execute_query(f"SELECT * FROM {table_name}")
        results = vector_search.search_vectors(df, query)
        return {"message": "Vector search completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
