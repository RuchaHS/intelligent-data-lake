from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from fastapi.responses import JSONResponse
import json
import pandas as pd
from pydantic import BaseModel
from models.metadata_analyzer_llm import MetadataAnalyzer
from models.query_optimizer import QueryOptimizer
from models.anomaly_detector import AnomalyDetector
from models.metadata_generator import MetadataGenerator
from models.data_quality_rules_generator import DataQualityGenerator
from pycaret.anomaly import setup, create_model, assign_model

app = FastAPI()

# ✅ Initialize Models
metadata_generator = MetadataGenerator()
query_optimizer = QueryOptimizer()
anomaly_detector = AnomalyDetector()
data_quality_generator = DataQualityGenerator()
metadata_analyzer = MetadataAnalyzer()

# ✅ Define Data Folders
data_folder = "uploads"
report_folder = os.path.abspath("profiling_reports")
os.makedirs(data_folder, exist_ok=True)
os.makedirs(report_folder, exist_ok=True)

# ✅ Serve Reports via FastAPI
app.mount("/profiling_reports", StaticFiles(directory=report_folder), name="profiling_reports")

class QueryRequest(BaseModel):
    query_text: str

@app.post("/text-to-sql")
def text_to_sql(request: QueryRequest):
    try:
        sql_query = query_optimizer.text_to_sql(request.query_text)
        return {"sql_query": sql_query}
    except Exception as e:
        logging.error(f"❌ Error generating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sql-to-text")
def sql_to_text(request: QueryRequest):
    try:
        explanation = query_optimizer.sql_to_text(request.query_text)
        return {"explanation": explanation}
    except Exception as e:
        logging.error(f"❌ Error explaining SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-metadata")
async def upload_file(file: UploadFile = File(...)):
    try:
        # ✅ Save Uploaded File
        file_path = os.path.join(data_folder, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # ✅ Generate Metadata & Profiling Report
        metadata = metadata_generator.generate_metadata(file_path)

        # ✅ Get Report Filename & URL
        report_filename = os.path.basename(metadata['profiling_report'])
        report_url = f"/profiling_reports/{report_filename}"

        # ✅ Ensure the Report Exists
        if not os.path.exists(metadata['profiling_report']):
            raise FileNotFoundError("Profiling report was not generated.")

        # ✅ Return JSON Response with Report Link & Embed Option
        return JSONResponse(
            content={
                "message": "Metadata processing successful.",
                "profiling_report_url": report_url,  # Opens in a new tab
                "embedded_report": f'<iframe src="{report_url}" width="100%" height="600px"></iframe>'  # Embeds in the UI
            },
            status_code=200
        )
    except FileNotFoundError as e:
        logging.error(f"❌ File Not Found: {str(e)}")
        return JSONResponse(content={"error": "File not found."}, status_code=404)
    except Exception as e:
        logging.error(f"❌ Error processing metadata: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


data_folder = "uploads"
report_folder = "anomaly_reports"
os.makedirs(data_folder, exist_ok=True)
os.makedirs(report_folder, exist_ok=True)

@app.post("/detect-anomalies")
async def detect_anomalies(file: UploadFile = File(...)):
    try:
        # ✅ Save Uploaded File
        file_path = os.path.join(data_folder, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # ✅ Load Data & Perform Anomaly Detection
        df = pd.read_csv(file_path)
        numeric_df = df.select_dtypes(include=["number"])

        if numeric_df.empty:
            raise ValueError("No numeric columns found in dataset for anomaly detection.")

        # ✅ PyCaret Setup & Model Creation
        setup(data=numeric_df, session_id=123, verbose=False)  # Removed `silent`
        model = create_model("iforest")
        anomalies_df = assign_model(model)

        # ✅ Filter for detected anomalies
        anomalies = anomalies_df[anomalies_df["Anomaly"] == 1].copy()

        # ✅ Save Detected Anomalies as CSV
        anomaly_csv_path = os.path.join(report_folder, f"anomalies_{file.filename}")
        anomalies.to_csv(anomaly_csv_path, index=False)

        # ✅ Return the CSV File URL
        return JSONResponse(
            content={
                "message": "Anomaly detection successful.",
                "anomaly_csv_url": f"/download-anomalies/{os.path.basename(anomaly_csv_path)}",
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"❌ Error detecting anomalies: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/download-anomalies/{filename}")
async def download_anomalies(filename: str):
    file_path = os.path.join(report_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="text/csv")
    else:
        raise HTTPException(status_code=404, detail="File not found.")

# NEW FEATURES
@app.post("/data-quality-rules")
async def data_quality_rules(file: UploadFile = File(...)):
    file_path = os.path.join(data_folder, file.filename)
    df = pd.read_csv(file_path)

    rules_json = data_quality_generator.generate_quality_rules(df)

    return JSONResponse(json.loads(rules_json))

@app.post("/metadata-llm")
async def metadata_llm(file: UploadFile = File(...)):
    file_path = os.path.join(data_folder, file.filename)
    df = pd.read_csv(file_path)

    analysis = metadata_analyzer.analyze_metadata(df)

    return JSONResponse({"metadata_analysis": analysis})