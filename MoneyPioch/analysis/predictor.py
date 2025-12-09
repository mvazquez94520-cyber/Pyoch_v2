#!/usr/bin/env python3
"""
Predictor Module for MoneyPioch
Handles analysis and prediction of sports outcomes
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class Predictor:
    """
    Main prediction class that analyzes sports data to generate predictions
    """
    
    def __init__(self):
        """
        Initialize the predictor with ML models
        """
        self.models = {
            'match_outcome': RandomForestClassifier(n_estimators=100, random_state=42),
            'player_performance': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'odds_movement': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Initialize feature names
        self.match_features = [
            'home_team_rating', 'away_team_rating', 'home_form', 'away_form',
            'head_to_head_home', 'head_to_head_away', 'home_goals_avg', 
            'away_goals_avg', 'home_def_avg', 'away_def_avg'
        ]
        
        self.player_features = [
            'minutes_played', 'goals', 'assists', 'shots_per_game', 
            'pass_accuracy', 'tackles_per_game', 'last_5_form_avg',
            'injury_risk', 'fatigue_factor'
        ]
    
    def analyze_data(self, raw_data: Dict) -> Dict:
        """
        Analyze raw sports data and generate predictions
        """
        logger.info("Starting data analysis and prediction...")
        
        # Process the raw data
        processed_data = self._process_raw_data(raw_data)
        
        # Generate different types of predictions
        match_predictions = self._predict_match_outcomes(processed_data)
        player_predictions = self._predict_player_performance(processed_data)
        odds_predictions = self._predict_odds_movements(processed_data)
        
        # Combine all predictions
        predictions = {
            'match_predictions': match_predictions,
            'player_predictions': player_predictions,
            'odds_predictions': odds_predictions,
            'timestamp': datetime.now()
        }
        
        logger.info("Analysis and prediction completed successfully")
        return predictions
    
    def _process_raw_data(self, raw_data: Dict) -> Dict:
        """
        Process raw data into a format suitable for prediction
        """
        logger.info("Processing raw data for analysis...")
        
        # Convert to DataFrames for easier manipulation
        matches_df = pd.DataFrame(raw_data.get('matches', []))
        players_df = pd.DataFrame(raw_data.get('players', []))
        teams_df = pd.DataFrame(raw_data.get('teams', []))
        odds_df = pd.DataFrame(raw_data.get('odds', []))
        historical_df = pd.DataFrame(raw_data.get('historical', []))
        
        # Create processed data structure
        processed = {
            'matches_df': matches_df,
            'players_df': players_df,
            'teams_df': teams_df,
            'odds_df': odds_df,
            'historical_df': historical_df
        }
        
        return processed
    
    def _predict_match_outcomes(self, processed_data: Dict) -> List[Dict]:
        """
        Predict match outcomes based on team statistics
        """
        logger.info("Predicting match outcomes...")
        
        matches_df = processed_data['matches_df']
        teams_df = processed_data['teams_df']
        historical_df = processed_data['historical_df']
        
        predictions = []
        
        for _, match in matches_df.iterrows():
            # Get team information
            home_team = teams_df[teams_df['name'] == match['home_team']].iloc[0] if len(teams_df[teams_df['name'] == match['home_team']]) > 0 else None
            away_team = teams_df[teams_df['name'] == match['away_team']].iloc[0] if len(teams_df[teams_df['name'] == match['away_team']]) > 0 else None
            
            if home_team is not None and away_team is not None:
                # Calculate features for prediction
                features = self._calculate_match_features(match, home_team, away_team, historical_df)
                
                # For now, we'll use a simple heuristic approach
                # In a real implementation, we would use trained ML models
                home_win_prob = self._calculate_home_win_probability(features)
                draw_prob = self._calculate_draw_probability(features)
                away_win_prob = 1 - home_win_prob - draw_prob  # Ensure probabilities sum to 1
                
                # Determine predicted winner
                if home_win_prob > away_win_prob and home_win_prob > draw_prob:
                    predicted_winner = 'home'
                    confidence = home_win_prob
                elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
                    predicted_winner = 'away'
                    confidence = away_win_prob
                else:
                    predicted_winner = 'draw'
                    confidence = draw_prob
                
                prediction = {
                    'match_id': match['id'],
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'predicted_winner': predicted_winner,
                    'home_win_probability': home_win_prob,
                    'draw_probability': draw_prob,
                    'away_win_probability': away_win_prob,
                    'confidence': confidence,
                    'expected_goals_home': self._predict_goals(features, 'home'),
                    'expected_goals_away': self._predict_goals(features, 'away')
                }
                
                predictions.append(prediction)
        
        return predictions
    
    def _calculate_match_features(self, match, home_team, away_team, historical_df) -> Dict:
        """
        Calculate features for match prediction
        """
        features = {}
        
        # Team ratings based on league position (inverse - lower position is better)
        features['home_team_rating'] = 21 - home_team['position']  # Higher rating for better position
        features['away_team_rating'] = 21 - away_team['position']
        
        # Form calculations (average points from last 5 games)
        features['home_form'] = np.mean(home_team['form']) if 'form' in home_team else 1.5
        features['away_form'] = np.mean(away_team['form']) if 'form' in away_team else 1.5
        
        # Goal statistics
        features['home_goals_avg'] = home_team['gf'] / home_team['games_played'] if home_team['games_played'] > 0 else 1.5
        features['away_goals_avg'] = away_team['gf'] / away_team['games_played'] if away_team['games_played'] > 0 else 1.5
        features['home_def_avg'] = home_team['ga'] / home_team['games_played'] if home_team['games_played'] > 0 else 1.5
        features['away_def_avg'] = away_team['ga'] / away_team['games_played'] if away_team['games_played'] > 0 else 1.5
        
        # Head-to-head from historical data
        h2h_matches = historical_df[
            ((historical_df['home_team'] == match['home_team']) & (historical_df['away_team'] == match['away_team'])) |
            ((historical_df['home_team'] == match['away_team']) & (historical_df['away_team'] == match['home_team']))
        ]
        
        features['head_to_head_home'] = len(h2h_matches[h2h_matches['winner'] == 'home']) if len(h2h_matches) > 0 else 0.5
        features['head_to_head_away'] = len(h2h_matches[h2h_matches['winner'] == 'away']) if len(h2h_matches) > 0 else 0.5
        
        # Additional factors
        features['home_advantage'] = 0.15  # Standard home advantage
        features['injury_impact_home'] = home_team.get('injuries', 0) * -0.05
        features['injury_impact_away'] = away_team.get('injuries', 0) * -0.05
        
        return features
    
    def _calculate_home_win_probability(self, features: Dict) -> float:
        """
        Calculate probability of home team winning
        """
        # Simple weighted calculation based on features
        rating_diff = features['home_team_rating'] - features['away_team_rating']
        form_diff = features['home_form'] - features['away_form']
        goal_diff = (features['home_goals_avg'] - features['away_def_avg']) - (features['away_goals_avg'] - features['home_def_avg'])
        
        # Combine factors with weights
        prob = 0.33 + (rating_diff * 0.02) + (form_diff * 0.05) + (goal_diff * 0.03) + features['home_advantage']
        
        # Apply injury impact
        prob += features['injury_impact_home'] - features['injury_impact_away']
        
        # Ensure probability is between 0 and 1
        return max(0.05, min(0.95, prob))
    
    def _calculate_draw_probability(self, features: Dict) -> float:
        """
        Calculate probability of match ending in a draw
        """
        # Calculate based on defensive strength similarity
        def_strength_diff = abs(features['home_def_avg'] - features['away_def_avg'])
        form_similarity = 1 - abs(features['home_form'] - features['away_form']) / 3.0  # Normalize form difference
        
        base_draw_prob = 0.25
        similarity_factor = 0.1 * form_similarity
        def_balance_factor = 0.05 * (1 - def_strength_diff/3.0)  # More balanced defenses lead to more draws
        
        prob = base_draw_prob + similarity_factor + def_balance_factor
        return max(0.05, min(0.4, prob))  # Draw probability typically between 5% and 40%
    
    def _predict_goals(self, features: Dict, team: str) -> float:
        """
        Predict expected goals for a team
        """
        if team == 'home':
            attack = features['home_goals_avg']
            defense = features['away_def_avg']
        else:  # away
            attack = features['away_goals_avg']
            defense = features['home_def_avg']
        
        # Simple average of attack strength and opposition defense weakness
        expected_goals = (attack + (3 - defense)) / 2  # Normalize defense (lower is better)
        
        # Add some randomness and home advantage for home team
        if team == 'home':
            expected_goals += features.get('home_advantage', 0) / 2
        
        return max(0, round(expected_goals, 1))
    
    def _predict_player_performance(self, processed_data: Dict) -> List[Dict]:
        """
        Predict individual player performance
        """
        logger.info("Predicting player performance...")
        
        players_df = processed_data['players_df']
        matches_df = processed_data['matches_df']
        
        predictions = []
        
        for _, player in players_df.iterrows():
            # Calculate performance metrics
            minutes_played_ratio = player.get('minutes_played', 0) / 2000  # Normalize against typical season minutes
            goals_per_90 = (player.get('goals', 0) * 90) / player.get('minutes_played', 1) if player.get('minutes_played', 1) > 0 else 0
            assists_per_90 = (player.get('assists', 0) * 90) / player.get('minutes_played', 1) if player.get('minutes_played', 1) > 0 else 0
            recent_form = np.mean(player.get('last_5_matches_form', [6.0])) if player.get('last_5_matches_form') else 6.0
            
            # Calculate injury risk (inverse of injury status)
            injury_risk = 0.1 if player.get('injury_status') == 'fit' else 0.8 if player.get('injury_status') == 'doubtful' else 0.95
            
            # Predict next match performance
            predicted_performance = {
                'player_id': player['id'],
                'player_name': player['name'],
                'team': player['team'],
                'position': player['position'],
                'predicted_minutes': min(90, player.get('minutes_played', 0) / 20 * 90),  # Predict based on average
                'predicted_goals': min(2, goals_per_90 * 1.1),  # Slight increase for next match
                'predicted_assists': min(3, assists_per_90 * 1.1),
                'predicted_rating': min(10, max(1, recent_form * 1.05)),  # Small form improvement
                'injury_risk': injury_risk,
                'confidence': 1 - injury_risk,
                'fitness_score': (1 - injury_risk) * 10
            }
            
            predictions.append(predicted_performance)
        
        return predictions
    
    def _predict_odds_movements(self, processed_data: Dict) -> List[Dict]:
        """
        Predict potential movements in betting odds
        """
        logger.info("Predicting odds movements...")
        
        odds_df = processed_data['odds_df']
        matches_df = processed_data['matches_df']
        
        predictions = []
        
        for _, odds in odds_df.iterrows():
            # Get the corresponding match
            match = matches_df[matches_df['id'] == odds['match_id']].iloc[0] if len(matches_df[matches_df['id'] == odds['match_id']]) > 0 else None
            
            if match is not None:
                # Calculate potential movement based on match importance, team form, etc.
                movement_prediction = {
                    'match_id': odds['match_id'],
                    'bookmaker': odds['bookmaker'],
                    'current_home_odds': odds['home_win'],
                    'current_draw_odds': odds['draw'],
                    'current_away_odds': odds['away_win'],
                    'predicted_home_movement': self._predict_odds_change(odds['home_win'], match),
                    'predicted_draw_movement': self._predict_odds_change(odds['draw'], match),
                    'predicted_away_movement': self._predict_odds_change(odds['away_win'], match),
                    'movement_confidence': 0.7  # Default confidence
                }
                
                predictions.append(movement_prediction)
        
        return predictions
    
    def _predict_odds_change(self, current_odds: float, match_info: pd.Series) -> float:
        """
        Predict how odds might change based on available information
        """
        # Simple model: if there's significant form difference, odds might shift
        # In a real implementation, this would be more sophisticated
        change = (np.random.random() - 0.5) * 0.2  # Random small change for demo
        return round(change, 3)
    
    def _calculate_risks(self, predictions: Dict) -> Dict:
        """
        Calculate risks associated with predictions
        """
        logger.info("Calculating prediction risks...")
        
        risks = {
            'high_confidence_predictions': [],
            'low_confidence_predictions': [],
            'volatile_markets': [],
            'injury_concerns': []
        }
        
        # Analyze match predictions for confidence levels
        for pred in predictions.get('match_predictions', []):
            if pred['confidence'] > 0.7:
                risks['high_confidence_predictions'].append(pred)
            elif pred['confidence'] < 0.4:
                risks['low_confidence_predictions'].append(pred)
        
        # Analyze player predictions for injury concerns
        for pred in predictions.get('player_predictions', []):
            if pred['injury_risk'] > 0.7:
                risks['injury_concerns'].append(pred)
        
        return risks