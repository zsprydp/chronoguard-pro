from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ChronoGuard Pro API",
    description="AI-Powered Appointment Optimization Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "ChronoGuard Pro",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "ChronoGuard Pro API is working!",
        "endpoints": [
            "GET / - Root endpoint",
            "GET /health - Health check",
            "GET /api/v1/test - This test endpoint",
            "GET /docs - API documentation"
        ]
    }