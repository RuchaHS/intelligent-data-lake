from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.query_optimizer import QueryOptimizer
from models.vector_search import VectorSearch
from models.anomaly_detector import AnomalyDetector
from models.metadata_generator import MetadataGenerator
from models.categorization import DataCategorizer

app = FastAPI()

metadata_generator = MetadataGenerator()
query_optimizer = QueryOptimizer()
anomaly_detector = AnomalyDetector()

class QueryRequest(BaseModel):
    query_text: str

@app.post("/text-to-sql")
def text_to_sql(request: QueryRequest):
    sql_query = query_optimizer.text_to_sql(request.query_text)
    return {"sql_query": sql_query}

@app.post("/sql-to-text")
def sql_to_text(request: QueryRequest):
    try:
        explanation = query_optimizer.sql_to_text(request.query_text)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Return proper error message

@app.get("/metadata")
def get_metadata():
    metadata = metadata_generator.generate_metadata("../data/sample_data.csv")
    return {"metadata": metadata}

# 📌 Upload CSV & Extract Metadata
@app.post("/upload-metadata")
async def upload_file(file: UploadFile = File(...)):
    try:
        # ✅ Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # ✅ Process metadata and profiling report
        metadata = metadata_generator.generate_metadata(file_path)

        return JSONResponse(content=metadata, status_code=200)

    except Exception as e:
        logging.error(f"❌ Error processing metadata: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/anomalies")
def detect_anomalies():
    anomalies = anomaly_detector.detect_anomalies("../data/sample_data.csv")
    return {"anomalies": anomalies.to_dict(orient="records")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
