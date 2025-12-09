"""
Data Collector for PYOCH Sportif
Handles data collection from various APIs and public sources
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import Athlete, PerformanceData, TrainingData, PublicInfo, SportType


class DataCollector:
    def __init__(self):
        self.session = None
        # Mock data for demonstration
        self.mock_athletes = {
            "athlete_001": {
                "athlete_id": "athlete_001",
                "name": "Marie Dupont",
                "age": 28,
                "gender": "F",
                "sport_type": SportType.RUNNING,
                "nationality": "FRA",
                "ranking": 5,
                "personal_best": 14.2,
                "injury_history": ["knee_injury_2022", "ankle_sprain_2023"],
                "training_location": "Paris",
                "coach": "Jean Martin",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        }
        
        self.mock_performances = {
            "athlete_001": [
                {
                    "performance_id": "perf_001",
                    "athlete_id": "athlete_001",
                    "date": datetime.now() - timedelta(days=7),
                    "event": "10km",
                    "result": 32.5,
                    "unit": "minutes",
                    "rank": 1,
                    "competition": "Paris 10km",
                    "weather_conditions": {"temperature": "18C", "wind": "5km/h"},
                    "notes": "Personal best"
                },
                {
                    "performance_id": "perf_002",
                    "athlete_id": "athlete_001",
                    "date": datetime.now() - timedelta(days=14),
                    "event": "10km",
                    "result": 33.1,
                    "unit": "minutes",
                    "rank": 2,
                    "competition": "Lyon Half Marathon",
                    "weather_conditions": {"temperature": "20C", "wind": "3km/h"},
                    "notes": "Good performance despite wind"
                }
            ]
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def collect_athlete_data(self, athlete_id: str, sport_type: SportType) -> Dict:
        """Collect athlete data from various sources"""
        # For demo purposes, return mock data
        if athlete_id in self.mock_athletes:
            athlete_data = self.mock_athletes[athlete_id].copy()
            athlete_data["sport_type"] = sport_type.value
            return athlete_data
        
        # In real implementation, this would fetch from:
        # - Sports federation APIs (e.g., World Athletics API)
        # - Olympic database APIs
        # - Athlete official websites
        # - Sports news APIs
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        return {
            "athlete_id": athlete_id,
            "name": f"Athlete {athlete_id}",
            "age": 25,
            "gender": "M",
            "sport_type": sport_type.value,
            "nationality": "FRA",
            "ranking": 10,
            "personal_best": 10.5,
            "injury_history": [],
            "training_location": "Unknown",
            "coach": "Unknown",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    async def collect_recent_performances(self, athlete_id: str, sport_type: SportType, days: int = 30) -> List[Dict]:
        """Collect recent performance data"""
        # For demo purposes, return mock data
        if athlete_id in self.mock_performances:
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_perfs = []
            for perf in self.mock_performances[athlete_id]:
                # Handle both datetime objects and ISO strings
                perf_date = perf["date"]
                if isinstance(perf_date, str):
                    perf_date = datetime.fromisoformat(perf_date.replace('Z', '+00:00'))
                if perf_date >= cutoff_date:
                    perf_copy = perf.copy()
                    perf_copy["date"] = perf_date.isoformat()
                    recent_perfs.append(perf_copy)
            return recent_perfs
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # In real implementation, this would fetch from:
        # - Competition results APIs
        # - Sports federation databases
        # - Timing system APIs
        
        return [
            {
                "performance_id": f"perf_{i}",
                "athlete_id": athlete_id,
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "event": "100m",
                "result": 10.5 + (i * 0.1),
                "unit": "seconds",
                "rank": i + 1,
                "competition": f"Competition {i}",
                "weather_conditions": {"temperature": f"{20+i}C", "wind": f"{i}km/h"},
                "notes": f"Performance note {i}"
            }
            for i in range(min(5, days))
        ]

    async def collect_training_data(self, athlete_id: str, sport_type: SportType) -> List[Dict]:
        """Collect training data from public sources"""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # In real implementation, this would fetch from:
        # - Training log APIs
        # - Wearable device APIs (Fitbit, Garmin, etc.)
        # - Coach training logs
        # - Public training session reports
        
        return [
            {
                "training_id": f"train_{i}",
                "athlete_id": athlete_id,
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "training_type": "endurance" if i % 2 == 0 else "speed",
                "duration_minutes": 90 + (i * 10),
                "intensity": 0.7 + (i * 0.05),
                "distance_km": 15.0 + (i * 2.0),
                "heart_rate_avg": 150 + i,
                "recovery_time_hours": 24 - (i * 2),
                "notes": f"Training session {i}"
            }
            for i in range(5)
        ]

    async def collect_public_info(self, athlete_id: str, sport_type: SportType) -> List[Dict]:
        """Collect public information from news, social media, etc."""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # In real implementation, this would fetch from:
        # - News APIs (NewsAPI, Guardian API, etc.)
        # - Social media APIs (Twitter, Instagram, etc.)
        # - Sports news websites
        # - Athlete official websites
        
        return [
            {
                "info_id": f"info_{i}",
                "athlete_id": athlete_id,
                "source": "news" if i % 3 == 0 else ("social_media" if i % 3 == 1 else "official"),
                "title": f"News about {athlete_id}",
                "content": f"Recent news article about athlete {athlete_id} and their preparation for upcoming competitions.",
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "sentiment_score": 0.5 + (i * 0.1) if i < 3 else -0.2,
                "relevance_score": 0.8 - (i * 0.1)
            }
            for i in range(3)
        ]

    async def get_athlete_info(self, athlete_id: str) -> Dict:
        """Get basic athlete information"""
        if athlete_id in self.mock_athletes:
            athlete_data = self.mock_athletes[athlete_id].copy()
            athlete_data["sport_type"] = athlete_data["sport_type"].value
            athlete_data["created_at"] = athlete_data["created_at"].isoformat()
            athlete_data["updated_at"] = athlete_data["updated_at"].isoformat()
            return athlete_data
            
        raise ValueError(f"Athlete with ID {athlete_id} not found")