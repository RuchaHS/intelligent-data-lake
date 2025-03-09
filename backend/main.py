from fastapi import FastAPI
# from routers import csv_routes, db_routes
from routers.csv_routes import router as csv_router
from routers.db_routes import router as db_router

app = FastAPI(title="Intelligent Data Lake with DuckDB")

# ✅ Include Routers
app.include_router(csv_router, prefix="/csv", tags=["CSV Processing"])
app.include_router(db_router, prefix="/db", tags=["Database Processing"])

@app.get("/")
def root():
    return {"message": "Welcome to Intelligent Data Lake"}
