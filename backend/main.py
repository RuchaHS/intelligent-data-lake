from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import csv_routes, db_routes

# ✅ Initialize FastAPI App
app = FastAPI(title="Intelligent Data Lake API", version="1.0")

# ✅ Allow CORS for Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include Routers
app.include_router(csv_routes.router)
app.include_router(db_routes.router)

# ✅ Root Route
@app.get("/")
def home():
    return {"message": "Welcome to Intelligent Data Lake API 🚀"}

# ✅ Health Check Route
@app.get("/health")
def health_check():
    return {"status": "Healthy", "message": "API is running smoothly!"}