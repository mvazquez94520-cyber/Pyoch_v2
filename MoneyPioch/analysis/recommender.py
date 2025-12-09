#!/usr/bin/env python3
"""
Recommender Module for MoneyPioch
Generates actionable recommendations based on predictions
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Recommender:
    """
    Main recommender class that generates actionable recommendations
    """
    
    def __init__(self):
        """
        Initialize the recommender system
        """
        self.betting_threshold = 0.65  # Minimum confidence for betting recommendation
        self.value_threshold = 0.1     # Minimum value threshold for betting
        self.risk_tolerance = 0.7      # Risk tolerance for recommendations
    
    def generate_recommendations(self, predictions: Dict) -> Dict:
        """
        Generate actionable recommendations from predictions
        """
        logger.info("Generating actionable recommendations...")
        
        # Generate different types of recommendations
        betting_recommendations = self._generate_betting_recommendations(predictions)
        team_recommendations = self._generate_team_recommendations(predictions)
        recruitment_recommendations = self._generate_recruitment_recommendations(predictions)
        risk_alerts = self._generate_risk_alerts(predictions)
        
        # Combine all recommendations
        recommendations = {
            'betting': betting_recommendations,
            'team_selection': team_recommendations,
            'recruitment': recruitment_recommendations,
            'risk_alerts': risk_alerts,
            'timestamp': datetime.now()
        }
        
        logger.info("Recommendations generated successfully")
        return recommendations
    
    def _generate_betting_recommendations(self, predictions: Dict) -> List[Dict]:
        """
        Generate betting recommendations based on match predictions and odds
        """
        logger.info("Generating betting recommendations...")
        
        recommendations = []
        match_predictions = predictions.get('match_predictions', [])
        
        for pred in match_predictions:
            # Calculate expected value for each outcome
            home_ev = self._calculate_expected_value(
                pred['home_win_probability'], 
                pred['confidence'], 
                pred.get('home_odds', pred['home_win_probability'] + 0.1)  # Fallback if no actual odds
            )
            
            draw_ev = self._calculate_expected_value(
                pred['draw_probability'], 
                pred['confidence'], 
                pred.get('draw_odds', pred['draw_probability'] + 0.1)
            )
            
            away_ev = self._calculate_expected_value(
                pred['away_win_probability'], 
                pred['confidence'], 
                pred.get('away_odds', pred['away_win_probability'] + 0.1)
            )
            
            # Find the best betting opportunity
            best_bet = max([('home', home_ev), ('draw', draw_ev), ('away', away_ev)], key=lambda x: x[1])
            
            if best_bet[1] > self.value_threshold and pred['confidence'] > self.betting_threshold:
                recommendation = {
                    'match_id': pred['match_id'],
                    'home_team': pred['home_team'],
                    'away_team': pred['away_team'],
                    'bet_on': best_bet[0],
                    'predicted_winner': pred['predicted_winner'],
                    'confidence': pred['confidence'],
                    'expected_value': best_bet[1],
                    'stake_suggestion': self._calculate_stake(best_bet[1], pred['confidence']),
                    'reasoning': self._generate_betting_reasoning(pred, best_bet[0])
                }
                
                recommendations.append(recommendation)
        
        # Sort by expected value
        recommendations.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return recommendations
    
    def _calculate_expected_value(self, probability: float, confidence: float, odds: float) -> float:
        """
        Calculate expected value of a bet
        """
        # Expected value = (probability * (odds - 1)) - ((1 - probability) * 1)
        # Adjusted by confidence level
        ev = (probability * (odds - 1)) - ((1 - probability) * 1)
        adjusted_ev = ev * confidence
        return max(0, adjusted_ev)  # Only return positive EV
    
    def _calculate_stake(self, expected_value: float, confidence: float) -> float:
        """
        Calculate recommended stake based on Kelly Criterion principles
        """
        # Simplified Kelly Criterion: stake = (expected_value * confidence) / 10
        # Max stake is 5% of bankroll
        stake = min(5.0, (expected_value * confidence) * 10)
        return round(stake, 2)
    
    def _generate_betting_reasoning(self, prediction: Dict, bet_on: str) -> str:
        """
        Generate reasoning for betting recommendation
        """
        if bet_on == 'home':
            return f"Home team has strong form and favorable statistics. Probability: {prediction['home_win_probability']:.2f}"
        elif bet_on == 'away':
            return f"Away team has better recent performance and tactical advantage. Probability: {prediction['away_win_probability']:.2f}"
        else:  # draw
            return f"Both teams appear evenly matched with balanced statistics. Probability: {prediction['draw_probability']:.2f}"
    
    def _generate_team_recommendations(self, predictions: Dict) -> List[Dict]:
        """
        Generate team formation and tactical recommendations
        """
        logger.info("Generating team formation recommendations...")
        
        recommendations = []
        player_predictions = predictions.get('player_predictions', [])
        match_predictions = predictions.get('match_predictions', [])
        
        # For each team, suggest optimal lineup
        teams = {}
        
        # Group players by team
        for player in player_predictions:
            team = player['team']
            if team not in teams:
                teams[team] = []
            teams[team].append(player)
        
        for team_name, players in teams.items():
            # Sort players by predicted performance and fitness
            sorted_players = sorted(players, 
                                  key=lambda x: x['predicted_rating'] * (1 - x['injury_risk']), 
                                  reverse=True)
            
            # Create position-based lineup
            lineup = self._create_optimal_lineup(sorted_players)
            
            recommendation = {
                'team': team_name,
                'formation': self._determine_formation(lineup),
                'starting_xi': lineup['starters'],
                'substitutes': lineup['subs'],
                'tactical_adjustments': self._suggest_tactical_adjustments(team_name, match_predictions),
                'key_players': self._identify_key_players(lineup['starters'])
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _create_optimal_lineup(self, players: List[Dict]) -> Dict:
        """
        Create an optimal lineup based on player predictions
        """
        # Position mappings
        positions = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
        
        # Categorize players by position
        for player in players:
            pos = player['position'].upper()
            if 'GOAL' in pos or 'GK' in pos:
                positions['GK'].append(player)
            elif 'DEF' in pos or 'BACK' in pos or 'CB' in pos or 'LB' in pos or 'RB' in pos:
                positions['DEF'].append(player)
            elif 'MID' in pos or 'MF' in pos:
                positions['MID'].append(player)
            else:  # Forward/Attacker
                positions['FWD'].append(player)
        
        # Select best players for each position
        starters = []
        subs = []
        
        # Goalkeeper
        if positions['GK']:
            starters.append(positions['GK'][0])
        
        # Defense (4 players)
        for i in range(min(4, len(positions['DEF']))):
            starters.append(positions['DEF'][i])
        
        # Midfield (4 players)
        for i in range(min(4, len(positions['MID']))):
            starters.append(positions['MID'][i])
        
        # Attack (2 players)
        for i in range(min(2, len(positions['FWD']))):
            starters.append(positions['FWD'][i])
        
        # Substitutes
        all_selected = [p['player_id'] for p in starters]
        for pos, pos_players in positions.items():
            for player in pos_players:
                if player['player_id'] not in all_selected and len(subs) < 7:
                    subs.append(player)
        
        return {'starters': starters, 'subs': subs}
    
    def _determine_formation(self, lineup: Dict) -> str:
        """
        Determine the formation based on selected players
        """
        def_count = len([p for p in lineup['starters'] if 'DEF' in p['position'].upper() or 'BACK' in p['position'].upper()])
        mid_count = len([p for p in lineup['starters'] if 'MID' in p['position'].upper()])
        fwd_count = len([p for p in lineup['starters'] if 'FWD' in p['position'].upper() or 'FORWARD' in p['position'].upper()])
        
        return f"{def_count}-{mid_count}-{fwd_count}"
    
    def _suggest_tactical_adjustments(self, team_name: str, match_predictions: List[Dict]) -> List[str]:
        """
        Suggest tactical adjustments based on upcoming opponent
        """
        adjustments = []
        
        # Find matches involving this team
        for match in match_predictions:
            if match['home_team'] == team_name or match['away_team'] == team_name:
                opponent = match['away_team'] if match['home_team'] == team_name else match['home_team']
                
                # Suggest based on opponent strength
                if match['home_win_probability'] > 0.6 and team_name == match['home_team']:
                    adjustments.append("Play aggressively, you're favored to win")
                elif match['away_win_probability'] > 0.6 and team_name == match['away_team']:
                    adjustments.append("Play aggressively, you're favored to win")
                elif match['home_win_probability'] > 0.6 and team_name == match['away_team']:
                    adjustments.append("Defend deep, opponent is favored")
                elif match['away_win_probability'] > 0.6 and team_name == match['home_team']:
                    adjustments.append("Defend deep, opponent is favored")
                else:
                    adjustments.append("Balanced approach, match is evenly poised")
                
                break
        
        return adjustments
    
    def _identify_key_players(self, starters: List[Dict]) -> List[Dict]:
        """
        Identify key players in the lineup
        """
        key_players = []
        
        for player in starters:
            if player['predicted_rating'] > 7.5 or player['fitness_score'] > 8:
                key_players.append({
                    'name': player['player_name'],
                    'position': player['position'],
                    'role': 'Key Player',
                    'importance_score': player['predicted_rating'] * player['fitness_score'] / 10
                })
        
        return key_players
    
    def _generate_recruitment_recommendations(self, predictions: Dict) -> List[Dict]:
        """
        Generate player recruitment recommendations
        """
        logger.info("Generating recruitment recommendations...")
        
        recommendations = []
        player_predictions = predictions.get('player_predictions', [])
        
        # Find undervalued players with high potential
        for player in player_predictions:
            # Calculate potential based on form, age (simulated), and performance
            potential_score = (
                player['predicted_rating'] * 0.4 + 
                (10 - player['injury_risk'] * 10) * 0.3 + 
                player['fitness_score'] * 0.3
            )
            
            # If potential significantly higher than current rating, recommend for recruitment
            if potential_score > player['predicted_rating'] + 1.0:
                recommendation = {
                    'player_name': player['player_name'],
                    'team_current': player['team'],
                    'position': player['position'],
                    'current_rating': player['predicted_rating'],
                    'potential_rating': potential_score,
                    'injury_risk': player['injury_risk'],
                    'recruitment_priority': 'high' if potential_score > 8.0 else 'medium',
                    'estimated_value': self._estimate_player_value(player, potential_score)
                }
                
                recommendations.append(recommendation)
        
        # Sort by potential and priority
        recommendations.sort(key=lambda x: x['potential_rating'], reverse=True)
        
        return recommendations
    
    def _estimate_player_value(self, player: Dict, potential: float) -> str:
        """
        Estimate player market value based on potential
        """
        if potential > 9.0:
            return "€50M+"
        elif potential > 8.0:
            return "€20M-50M"
        elif potential > 7.0:
            return "€8M-20M"
        elif potential > 6.0:
            return "€3M-8M"
        else:
            return "€1M-3M"
    
    def _generate_risk_alerts(self, predictions: Dict) -> List[Dict]:
        """
        Generate risk alerts based on predictions
        """
        logger.info("Generating risk alerts...")
        
        alerts = []
        
        # Check for high-risk bets
        for bet in predictions.get('betting_recommendations', []):
            if bet['expected_value'] < 0.05:  # Very low value
                alerts.append({
                    'type': 'betting_risk',
                    'severity': 'high',
                    'message': f"Low value bet recommended on {bet['home_team']} vs {bet['away_team']}",
                    'details': f"Expected value is only {bet['expected_value']:.3f}"
                })
        
        # Check for injury concerns
        for player in predictions.get('player_predictions', []):
            if player['injury_risk'] > 0.8:
                alerts.append({
                    'type': 'injury_concern',
                    'severity': 'high',
                    'message': f"High injury risk for {player['player_name']}",
                    'details': f"Injury risk: {player['injury_risk']:.2f}, fitness score: {player['fitness_score']:.2f}"
                })
        
        # Check for uncertain match predictions
        for match in predictions.get('match_predictions', []):
            if match['confidence'] < 0.4:
                alerts.append({
                    'type': 'prediction_uncertainty',
                    'severity': 'medium',
                    'message': f"Uncertain prediction for {match['home_team']} vs {match['away_team']}",
                    'details': f"Confidence level: {match['confidence']:.2f}"
                })
        
        return alerts