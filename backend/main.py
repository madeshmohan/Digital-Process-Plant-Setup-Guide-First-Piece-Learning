import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router
from backend.database.database import init_db, seed_default_products, get_db_connection
from data.generate_dataset import generate_synthetic_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_default_products()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM setups")
    count = cursor.fetchone()["count"]
    conn.close()
    if count < 500:
        print("Database contains insufficient setup records. Generating synthetic dataset (750 records)...")
        generate_synthetic_data(750)
    print("FastAPI Backend ready at http://localhost:8000")
    print("API Documentation available at http://localhost:8000/docs")
    yield

app = FastAPI(
    title="Process Plant Digital Setup Guide API",
    description="API server for parameter validation, non-linear T-P interaction envelope, first-piece learning, and offline sync.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Process Plant Digital Setup Guide API Server Running",
        "docs": "http://localhost:8000/docs",
        "disclaimer": "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results are synthetic demonstration assumptions and must not be used as real plant operating instructions."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
