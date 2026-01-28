"""
Main FastAPI application.

Consent-Aware AI Debug & Evaluation Dashboard - Backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import ai, consent, logs

app = FastAPI(
    title="Consent-Aware AI Dashboard API",
    description="Backend API for debugging and evaluating AI systems with consent-aware data access",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(consent.router)
app.include_router(ai.router)
app.include_router(logs.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Consent-Aware AI Debug & Evaluation Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "consent": "/consent",
            "ai": "/ai",
            "logs": "/logs",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
