from fastapi import FastAPI
from features.migrations.routes import router as migrations_router
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Weather API")

app.include_router(migrations_router, prefix="/api/migrations", tags=["migrations"])



@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather API!"}
