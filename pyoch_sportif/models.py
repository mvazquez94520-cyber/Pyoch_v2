"""
Models for PYOCH Sportif - Sports Performance Prediction
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class SportType(str, Enum):
    ATHLETICS = "athletics"
    SWIMMING = "swimming"
    CYCLING = "cycling"
    RUNNING = "running"
    TENNIS = "tennis"
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    WEIGHTLIFTING = "weightlifting"
    MARTIAL_ARTS = "martial_arts"


class Athlete(BaseModel):
    athlete_id: str
    name: str
    age: int
    gender: str
    sport_type: SportType
    nationality: str
    ranking: Optional[int] = None
    personal_best: Optional[float] = None
    injury_history: List[str] = []
    training_location: Optional[str] = None
    coach: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PerformanceData(BaseModel):
    performance_id: str
    athlete_id: str
    date: datetime
    event: str
    result: float
    unit: str  # seconds, meters, kg, etc.
    rank: Optional[int] = None
    competition: Optional[str] = None
    weather_conditions: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


class TrainingData(BaseModel):
    training_id: str
    athlete_id: str
    date: datetime
    training_type: str
    duration_minutes: int
    intensity: float  # 0.0 to 1.0
    distance_km: Optional[float] = None
    heart_rate_avg: Optional[int] = None
    recovery_time_hours: Optional[float] = None
    notes: Optional[str] = None


class PublicInfo(BaseModel):
    info_id: str
    athlete_id: str
    source: str  # news, social_media, official_website
    title: str
    content: str
    date: datetime
    sentiment_score: float  # -1.0 to 1.0
    relevance_score: float  # 0.0 to 1.0


class PredictionRequest(BaseModel):
    athlete_id: str
    sport_type: SportType
    competition_date: datetime
    time_range_days: int = 30  # Days of historical data to consider
    additional_factors: Optional[Dict[str, str]] = None


class PredictionResult(BaseModel):
    performance_score: float
    confidence: float  # 0.0 to 1.0
    risk_factors: List[str]
    recommendations: List[str]
    data_sources: List[str]


class PredictionResponse(BaseModel):
    athlete_id: str
    sport_type: SportType
    predicted_performance: float
    confidence_level: float
    risk_factors: List[str]
    recommendations: List[str]
    prediction_date: str
    data_sources: List[str]


class Competition(BaseModel):
    competition_id: str
    name: str
    sport_type: SportType
    location: str
    start_date: datetime
    end_date: datetime
    category: str  # olympic, world_championship, national, etc.
    participants_count: Optional[int] = None
    prize_money: Optional[float] = None