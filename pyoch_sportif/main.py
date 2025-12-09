"""
PYOCH - Template Sportif
Système de prédiction des performances sportives pour athlètes de haut niveau
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from data_collector import DataCollector
from prediction_engine import PredictionEngine
from models import Athlete, PerformanceData, PredictionRequest, PredictionResponse

app = FastAPI(
    title="PYOCH - Template Sportif",
    description="Système de prédiction des performances sportives pour athlètes de haut niveau",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
data_collector = DataCollector()
prediction_engine = PredictionEngine()

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/collect-data")
async def collect_data(request: PredictionRequest):
    """Collect data from various sources (APIs, public sources)"""
    try:
        athlete_data = await data_collector.collect_athlete_data(
            request.athlete_id,
            request.sport_type
        )
        
        # Collect recent performance data
        recent_performances = await data_collector.collect_recent_performances(
            request.athlete_id,
            request.sport_type,
            request.time_range_days
        )
        
        # Collect training data from public sources
        training_data = await data_collector.collect_training_data(
            request.athlete_id,
            request.sport_type
        )
        
        # Collect news and public information
        public_info = await data_collector.collect_public_info(
            request.athlete_id,
            request.sport_type
        )
        
        return {
            "athlete_data": athlete_data,
            "recent_performances": recent_performances,
            "training_data": training_data,
            "public_info": public_info,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-performance")
async def predict_performance(request: PredictionRequest):
    """Predict athlete performance based on collected data"""
    try:
        # Collect all necessary data
        athlete_data = await data_collector.collect_athlete_data(
            request.athlete_id,
            request.sport_type
        )
        
        recent_performances = await data_collector.collect_recent_performances(
            request.athlete_id,
            request.sport_type,
            request.time_range_days
        )
        
        training_data = await data_collector.collect_training_data(
            request.athlete_id,
            request.sport_type
        )
        
        public_info = await data_collector.collect_public_info(
            request.athlete_id,
            request.sport_type
        )
        
        # Generate prediction
        prediction = prediction_engine.predict_performance(
            athlete_data,
            recent_performances,
            training_data,
            public_info,
            request.competition_date
        )
        
        return PredictionResponse(
            athlete_id=request.athlete_id,
            sport_type=request.sport_type,
            predicted_performance=prediction.performance_score,
            confidence_level=prediction.confidence,
            risk_factors=prediction.risk_factors,
            recommendations=prediction.recommendations,
            prediction_date=datetime.now().isoformat(),
            data_sources=prediction.data_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/athlete/{athlete_id}")
async def get_athlete(athlete_id: str):
    """Get athlete information"""
    try:
        athlete = await data_collector.get_athlete_info(athlete_id)
        return athlete
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    print("Démarrage du serveur PYOCH - Template Sportif...")
    print("L'API sera disponible à l'adresse: http://localhost:8000")
    print("Interface web: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)