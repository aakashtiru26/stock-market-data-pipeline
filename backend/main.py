import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stocks, pipeline, analytics
from models.database import engine, Base
from pipeline.scheduler import start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables if they don't exist
# In a real production app, use Alembic for migrations instead
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Market Data Pipeline API",
    description="Backend for ETL and Data Serving",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(stocks.router)
app.include_router(pipeline.router)
app.include_router(analytics.router)

@app.on_event("startup")
def startup_event():
    logger.info("Starting up FastAPI application...")
    # Start the APScheduler
    app.state.scheduler = start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down FastAPI application...")
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Market Data Pipeline API. Check /docs for endpoints."}
