from fastapi import APIRouter, HTTPException
from models.query_optimizer import QueryOptimizer
import duckdb

router = APIRouter(prefix="/db", tags=["Database Processing"])

# ✅ Connect to DuckDB
DB_PATH = "intelligent_data_lake.duckdb"
conn = duckdb.connect(DB_PATH)

# ✅ Initialize Query Optimizer Model
query_optimizer = QueryOptimizer()


def execute_query(query: str):
    """Executes a SQL query in DuckDB and returns results as a list of dictionaries."""
    try:
        return conn.execute(query).fetchdf().to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Text-to-SQL (Convert NL to SQL)
@router.post("/text-to-sql")
def text_to_sql(query_text: str):
    try:
        sql_query = query_optimizer.text_to_sql(query_text)
        return {"sql_query": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ SQL-to-Text (Explain SQL)
@router.post("/sql-to-text")
def sql_to_text(query_text: str):
    try:
        explanation = query_optimizer.sql_to_text(query_text)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Run SQL Query
@router.post("/run-query")
def run_query(query_text: str):
    try:
        results = execute_query(query_text)
        return {"query_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ List Tables
@router.get("/list-tables")
def list_tables():
    try:
        tables = conn.execute("SHOW TABLES").fetchdf()["name"].tolist()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Preview Table
@router.get("/preview-table/{table_name}")
def preview_table(table_name: str):
    try:
        preview_query = f"SELECT * FROM {table_name} LIMIT 10"
        preview = execute_query(preview_query)
        return {"preview": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
