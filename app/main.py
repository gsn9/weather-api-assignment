# app/main.py
from fastapi import FastAPI
from app.routes.ingestion_routes import router as ingestion_router
from app.routes.migrations_routes import router as migration_router
from app.routes.weather_routes import router as weather_router
from app.db.database import init_db
from app.utils.logger import setup_logging

app = FastAPI(title="ETL Pipeline API")

# Setup logging
setup_logging()

@app.on_event("startup")
async def on_startup():
    await init_db()

# Include routers
app.include_router(ingestion_router, prefix="/api")
app.include_router(migration_router, prefix="/api")
app.include_router(weather_router, prefix="/api")