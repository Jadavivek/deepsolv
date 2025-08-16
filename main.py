"""
Shopify Store Insights Fetcher Application
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.api.routes import insights
from app.core.config import settings
from app.database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="Extract comprehensive insights from Shopify stores without using official APIs",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(insights.router, prefix="/api/v1", tags=["insights"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Shopify Store Insights Fetcher API",
        "version": "1.0.0",
        "status": "active"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
