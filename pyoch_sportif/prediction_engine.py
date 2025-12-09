"""
Prediction Engine for PYOCH Sportif
Uses collected data to predict athlete performance
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List
from models import PredictionResult


class PredictionEngine:
    def __init__(self):
        # Weights for different factors in performance prediction
        self.performance_weight = 0.4
        self.training_weight = 0.25
        self.public_info_weight = 0.15
        self.injury_weight = 0.2
        
    def predict_performance(
        self,
        athlete_data: Dict,
        recent_performances: List[Dict],
        training_data: List[Dict],
        public_info: List[Dict],
        competition_date: datetime
    ) -> PredictionResult:
        """
        Predict athlete performance based on collected data
        """
        # Calculate base performance from recent performances
        base_performance = self._calculate_base_performance(recent_performances)
        
        # Calculate training impact
        training_impact = self._calculate_training_impact(training_data)
        
        # Calculate public info sentiment impact
        sentiment_impact = self._calculate_sentiment_impact(public_info)
        
        # Calculate injury risk
        injury_risk = self._calculate_injury_risk(athlete_data)
        
        # Calculate time to competition factor
        time_factor = self._calculate_time_factor(competition_date)
        
        # Combine all factors to predict performance
        predicted_performance = (
            base_performance * self.performance_weight +
            training_impact * self.training_weight +
            sentiment_impact * self.public_info_weight +
            injury_risk * self.injury_weight
        ) * time_factor
        
        # Calculate confidence based on data availability and recency
        confidence = self._calculate_confidence(
            recent_performances, training_data, public_info
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            athlete_data, recent_performances, training_data, public_info
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            athlete_data, recent_performances, training_data, public_info
        )
        
        # Determine data sources used
        data_sources = []
        if recent_performances:
            data_sources.append("competition_results_api")
        if training_data:
            data_sources.append("training_logs_api")
        if public_info:
            data_sources.append("news_and_social_media")
        data_sources.append("athlete_profile_api")
        
        return PredictionResult(
            performance_score=predicted_performance,
            confidence=confidence,
            risk_factors=risk_factors,
            recommendations=recommendations,
            data_sources=data_sources
        )
    
    def _calculate_base_performance(self, recent_performances: List[Dict]) -> float:
        """Calculate base performance from recent results"""
        if not recent_performances:
            return 10.0  # Default baseline
        
        # Sort performances by date (most recent first)
        sorted_performances = sorted(
            recent_performances,
            key=lambda x: datetime.fromisoformat(x['date']),
            reverse=True
        )
        
        # Calculate weighted average of recent performances
        total_weight = 0
        weighted_sum = 0
        
        for i, perf in enumerate(sorted_performances):
            # More recent performances have higher weight
            weight = 1.0 / (i + 1)  # Recent performances weighted more
            weighted_sum += perf['result'] * weight
            total_weight += weight
        
        if total_weight > 0:
            base_performance = weighted_sum / total_weight
        else:
            base_performance = 10.0
        
        # Add some randomness to simulate uncertainty
        base_performance *= (1 + random.uniform(-0.05, 0.05))
        
        return base_performance
    
    def _calculate_training_impact(self, training_data: List[Dict]) -> float:
        """Calculate impact of training on performance"""
        if not training_data:
            return 1.0  # Neutral impact
        
        # Calculate average training intensity
        total_intensity = sum(t['intensity'] for t in training_data)
        avg_intensity = total_intensity / len(training_data)
        
        # Calculate average training duration
        total_duration = sum(t['duration_minutes'] for t in training_data)
        avg_duration = total_duration / len(training_data)
        
        # Normalize to 0-1 scale where higher is better
        # Assuming optimal training intensity is around 0.7-0.8
        intensity_factor = min(1.2, max(0.8, avg_intensity / 0.7))
        
        # Assuming optimal training duration is around 90 minutes
        duration_factor = min(1.2, max(0.8, avg_duration / 90.0))
        
        # Combine factors
        training_impact = (intensity_factor + duration_factor) / 2
        
        return training_impact
    
    def _calculate_sentiment_impact(self, public_info: List[Dict]) -> float:
        """Calculate impact of public sentiment on performance"""
        if not public_info:
            return 1.0  # Neutral impact
        
        # Calculate average sentiment score
        total_sentiment = sum(info['sentiment_score'] for info in public_info)
        avg_sentiment = total_sentiment / len(public_info)
        
        # Convert sentiment to performance impact
        # Positive sentiment (0.5 to 1.0) improves performance
        # Negative sentiment (-1.0 to -0.5) reduces performance
        if avg_sentiment > 0.2:
            # Positive sentiment gives slight performance boost
            sentiment_impact = 1.0 + (avg_sentiment * 0.1)
        elif avg_sentiment < -0.2:
            # Negative sentiment slightly reduces performance
            sentiment_impact = 1.0 + (avg_sentiment * 0.05)
        else:
            # Neutral sentiment
            sentiment_impact = 1.0
        
        return sentiment_impact
    
    def _calculate_injury_risk(self, athlete_data: Dict) -> float:
        """Calculate injury risk impact on performance"""
        injury_history = athlete_data.get('injury_history', [])
        
        if not injury_history:
            return 1.0  # No injury risk
        
        # More injuries = higher risk = lower performance
        injury_risk = 1.0 - (len(injury_history) * 0.05)
        injury_risk = max(0.7, injury_risk)  # Minimum 70% performance impact
        
        return injury_risk
    
    def _calculate_time_factor(self, competition_date: datetime) -> float:
        """Calculate time to competition impact on performance"""
        days_to_competition = (competition_date - datetime.now()).days
        
        if days_to_competition < 0:
            # Competition has passed
            return 0.0
        elif days_to_competition <= 7:
            # Competition is very soon - possible tapering effect
            return 1.05  # Slight performance boost due to peak training
        elif days_to_competition <= 30:
            # Good preparation window
            return 1.0
        elif days_to_competition <= 90:
            # Longer term planning
            return 0.98  # Slight uncertainty factor
        else:
            # Very long term prediction - high uncertainty
            return 0.95
    
    def _calculate_confidence(
        self,
        recent_performances: List[Dict],
        training_data: List[Dict],
        public_info: List[Dict]
    ) -> float:
        """Calculate confidence level in the prediction"""
        # Base confidence
        confidence = 0.5
        
        # Add confidence based on data availability
        if len(recent_performances) >= 5:
            confidence += 0.2
        elif len(recent_performances) >= 2:
            confidence += 0.1
        # Maximum 0.2 from performance data
        
        if len(training_data) >= 10:
            confidence += 0.15
        elif len(training_data) >= 5:
            confidence += 0.1
        # Maximum 0.15 from training data
        
        if len(public_info) >= 3:
            confidence += 0.1
        elif len(public_info) >= 1:
            confidence += 0.05
        # Maximum 0.1 from public info
        
        # Ensure confidence doesn't exceed 0.95 (always some uncertainty in sports)
        confidence = min(0.95, confidence)
        
        # Add some randomness to reflect inherent uncertainty in sports
        confidence += random.uniform(-0.05, 0.05)
        confidence = max(0.1, min(0.95, confidence))
        
        return confidence
    
    def _identify_risk_factors(
        self,
        athlete_data: Dict,
        recent_performances: List[Dict],
        training_data: List[Dict],
        public_info: List[Dict]
    ) -> List[str]:
        """Identify potential risk factors for performance"""
        risk_factors = []
        
        # Check injury history
        if athlete_data.get('injury_history'):
            risk_factors.append(f"History of {len(athlete_data['injury_history'])} injuries")
        
        # Check recent performance trends
        if len(recent_performances) >= 3:
            sorted_perfs = sorted(
                recent_performances,
                key=lambda x: datetime.fromisoformat(x['date'])
            )
            # Compare first and last performance
            if len(sorted_perfs) >= 2:
                first_perf = sorted_perfs[0]['result']
                last_perf = sorted_perfs[-1]['result']
                # Assuming lower result is better (e.g., running time)
                if last_perf > first_perf * 1.05:  # Performance has declined by 5%
                    risk_factors.append("Declining performance trend")
        
        # Check training load
        if training_data:
            avg_intensity = sum(t['intensity'] for t in training_data) / len(training_data)
            if avg_intensity > 0.9:
                risk_factors.append("High training intensity - risk of overtraining")
            elif avg_intensity < 0.5:
                risk_factors.append("Low training intensity - may affect performance")
        
        # Check public sentiment
        if public_info:
            avg_sentiment = sum(info['sentiment_score'] for info in public_info) / len(public_info)
            if avg_sentiment < -0.3:
                risk_factors.append("Negative public sentiment affecting confidence")
        
        if not risk_factors:
            risk_factors.append("No significant risk factors identified")
        
        return risk_factors
    
    def _generate_recommendations(
        self,
        athlete_data: Dict,
        recent_performances: List[Dict],
        training_data: List[Dict],
        public_info: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on the data analysis"""
        recommendations = []
        
        # Training recommendations
        if training_data:
            avg_intensity = sum(t['intensity'] for t in training_data) / len(training_data)
            if avg_intensity > 0.85:
                recommendations.append("Consider reducing training intensity to prevent overtraining")
            elif avg_intensity < 0.6:
                recommendations.append("Consider increasing training intensity for better preparation")
        
        # Performance trend recommendations
        if len(recent_performances) >= 3:
            sorted_perfs = sorted(
                recent_performances,
                key=lambda x: datetime.fromisoformat(x['date'])
            )
            if len(sorted_perfs) >= 2:
                first_perf = sorted_perfs[0]['result']
                last_perf = sorted_perfs[-1]['result']
                if last_perf > first_perf * 1.02:  # Performance declined
                    recommendations.append("Focus on technique improvement to reverse declining trend")
                elif last_perf < first_perf * 0.98:  # Performance improved
                    recommendations.append("Continue current training approach - showing positive results")
        
        # Recovery recommendations
        if training_data:
            recent_trainings = sorted(
                training_data,
                key=lambda x: datetime.fromisoformat(x['date']),
                reverse=True
            )[:3]  # Last 3 training sessions
            
            if recent_trainings:
                avg_recovery = sum(t.get('recovery_time_hours', 0) for t in recent_trainings) / len(recent_trainings)
                if avg_recovery < 20:
                    recommendations.append("Ensure adequate recovery time between intensive sessions")
        
        # Competition preparation recommendations
        recommendations.append("Monitor injury status closely as competition approaches")
        recommendations.append("Maintain consistent training routine in final weeks")
        
        if not recommendations:
            recommendations.append("Maintain current training and preparation approach")
        
        return recommendations