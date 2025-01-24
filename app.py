from fastapi import FastAPI
# from features.weather.routes import weather_router
# from features.stats.routes import stats_router
# from db.database import Base, engine

app = FastAPI(title="Weather API")



@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather API!"}
