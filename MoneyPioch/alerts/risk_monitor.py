#!/usr/bin/env python3
"""
Risk Monitor Module for MoneyPioch
Monitors and alerts on potential risks
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class RiskMonitor:
    """
    Main risk monitoring class that tracks and alerts on potential risks
    """
    
    def __init__(self):
        """
        Initialize the risk monitoring system
        """
        self.risk_thresholds = {
            'high_confidence_low_value': 0.7,  # High confidence but low expected value
            'market_volatility': 0.3,          # Threshold for odds movement
            'injury_risk': 0.7,                # Threshold for high injury risk
            'prediction_uncertainty': 0.4,     # Low confidence threshold
            'betting_exposure': 10.0           # Max percentage of bankroll to risk
        }
        
        self.alert_history = []
        self.current_alerts = []
    
    def check_for_risks(self, predictions: Dict) -> List[Dict]:
        """
        Check predictions for potential risks and generate alerts
        """
        logger.info("Checking for potential risks...")
        
        alerts = []
        
        # Check match prediction risks
        match_alerts = self._check_match_prediction_risks(predictions.get('match_predictions', []))
        alerts.extend(match_alerts)
        
        # Check player risks
        player_alerts = self._check_player_risks(predictions.get('player_predictions', []))
        alerts.extend(player_alerts)
        
        # Check odds movement risks
        odds_alerts = self._check_odds_risks(predictions.get('odds_predictions', []))
        alerts.extend(odds_alerts)
        
        # Update current alerts
        self.current_alerts = alerts
        self.alert_history.extend(alerts)
        
        logger.info(f"Risk check completed. {len(alerts)} alerts generated.")
        return alerts
    
    def _check_match_prediction_risks(self, match_predictions: List[Dict]) -> List[Dict]:
        """
        Check for risks in match predictions
        """
        alerts = []
        
        for pred in match_predictions:
            # Check for high confidence but low expected value (potentially misleading)
            if pred['confidence'] > self.risk_thresholds['high_confidence_low_value']:
                # Calculate expected value based on provided odds (if available)
                home_odds = pred.get('home_odds', pred['home_win_probability'] + 0.1)
                draw_odds = pred.get('draw_odds', pred['draw_probability'] + 0.1)
                away_odds = pred.get('away_odds', pred['away_win_probability'] + 0.1)
                
                # Calculate EV for the predicted outcome
                if pred['predicted_winner'] == 'home':
                    ev = (pred['home_win_probability'] * (home_odds - 1)) - ((1 - pred['home_win_probability']) * 1)
                elif pred['predicted_winner'] == 'draw':
                    ev = (pred['draw_probability'] * (draw_odds - 1)) - ((1 - pred['draw_probability']) * 1)
                else:  # away
                    ev = (pred['away_win_probability'] * (away_odds - 1)) - ((1 - pred['away_win_probability']) * 1)
                
                if ev < 0.1:  # Low expected value despite high confidence
                    alerts.append({
                        'id': f"match_risk_{pred['match_id']}_low_ev",
                        'type': 'low_expected_value',
                        'severity': 'medium',
                        'match': f"{pred['home_team']} vs {pred['away_team']}",
                        'message': f"High confidence prediction ({pred['confidence']:.2f}) has low expected value ({ev:.3f})",
                        'timestamp': datetime.now(),
                        'details': {
                            'confidence': pred['confidence'],
                            'expected_value': ev,
                            'predicted_outcome': pred['predicted_winner']
                        }
                    })
            
            # Check for prediction uncertainty
            if pred['confidence'] < self.risk_thresholds['prediction_uncertainty']:
                alerts.append({
                    'id': f"match_risk_{pred['match_id']}_uncertainty",
                    'type': 'prediction_uncertainty',
                    'severity': 'high',
                    'match': f"{pred['home_team']} vs {pred['away_team']}",
                    'message': f"Low confidence prediction ({pred['confidence']:.2f}) for {pred['home_team']} vs {pred['away_team']}",
                    'timestamp': datetime.now(),
                    'details': {
                        'confidence': pred['confidence'],
                        'home_prob': pred['home_win_probability'],
                        'draw_prob': pred['draw_probability'],
                        'away_prob': pred['away_win_probability']
                    }
                })
        
        return alerts
    
    def _check_player_risks(self, player_predictions: List[Dict]) -> List[Dict]:
        """
        Check for risks related to player predictions
        """
        alerts = []
        
        for player in player_predictions:
            # Check for high injury risk
            if player['injury_risk'] > self.risk_thresholds['injury_risk']:
                alerts.append({
                    'id': f"player_risk_{player['player_id']}_injury",
                    'type': 'injury_concern',
                    'severity': 'high',
                    'player': player['player_name'],
                    'team': player['team'],
                    'message': f"High injury risk ({player['injury_risk']:.2f}) for {player['player_name']}",
                    'timestamp': datetime.now(),
                    'details': {
                        'injury_risk': player['injury_risk'],
                        'fitness_score': player['fitness_score'],
                        'position': player['position']
                    }
                })
            
            # Check for inconsistent performance
            if player['predicted_rating'] < 6.0 and player.get('last_5_form_avg', 7.0) > 7.5:
                alerts.append({
                    'id': f"player_risk_{player['player_id']}_form",
                    'type': 'performance_concern',
                    'severity': 'medium',
                    'player': player['player_name'],
                    'team': player['team'],
                    'message': f"Predicted decline for {player['player_name']} (recent form: {player.get('last_5_form_avg', 0):.2f}, predicted: {player['predicted_rating']:.2f})",
                    'timestamp': datetime.now(),
                    'details': {
                        'recent_form': player.get('last_5_form_avg', 0),
                        'predicted_rating': player['predicted_rating'],
                        'position': player['position']
                    }
                })
        
        return alerts
    
    def _check_odds_risks(self, odds_predictions: List[Dict]) -> List[Dict]:
        """
        Check for risks related to odds movements
        """
        alerts = []
        
        for pred in odds_predictions:
            # Check for high volatility in odds
            max_movement = max(
                abs(pred['predicted_home_movement']),
                abs(pred['predicted_draw_movement']),
                abs(pred['predicted_away_movement'])
            )
            
            if max_movement > self.risk_thresholds['market_volatility']:
                alerts.append({
                    'id': f"odds_risk_{pred['match_id']}_volatility",
                    'type': 'market_volatility',
                    'severity': 'medium',
                    'match': f"Match {pred['match_id']}",
                    'message': f"High odds volatility predicted for {pred['bookmaker']} market",
                    'timestamp': datetime.now(),
                    'details': {
                        'home_movement': pred['predicted_home_movement'],
                        'draw_movement': pred['predicted_draw_movement'],
                        'away_movement': pred['predicted_away_movement'],
                        'bookmaker': pred['bookmaker']
                    }
                })
        
        return alerts
    
    def get_alert_summary(self) -> Dict:
        """
        Get a summary of current alerts
        """
        summary = {
            'total_alerts': len(self.current_alerts),
            'high_severity': len([a for a in self.current_alerts if a['severity'] == 'high']),
            'medium_severity': len([a for a in self.current_alerts if a['severity'] == 'medium']),
            'low_severity': len([a for a in self.current_alerts if a['severity'] == 'low']),
            'by_type': {}
        }
        
        # Count alerts by type
        for alert in self.current_alerts:
            alert_type = alert['type']
            if alert_type not in summary['by_type']:
                summary['by_type'][alert_type] = 0
            summary['by_type'][alert_type] += 1
        
        return summary
    
    def generate_risk_report(self) -> str:
        """
        Generate a comprehensive risk report
        """
        summary = self.get_alert_summary()
        
        report = f"""
# MoneyPioch Risk Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Risk Summary
- Total Active Alerts: {summary['total_alerts']}
- High Severity: {summary['high_severity']}
- Medium Severity: {summary['medium_severity']}
- Low Severity: {summary['low_severity']}

## Alerts by Type
"""
        
        for alert_type, count in summary['by_type'].items():
            report += f"- {alert_type.replace('_', ' ').title()}: {count}\n"
        
        report += "\n## Detailed Alerts\n"
        
        for alert in self.current_alerts:
            report += f"- [{alert['severity'].upper()}] {alert['message']}\n"
            report += f"  Type: {alert['type']}, Time: {alert['timestamp']}\n"
            if 'match' in alert:
                report += f"  Match: {alert['match']}\n"
            elif 'player' in alert:
                report += f"  Player: {alert['player']} ({alert['team']})\n"
            report += "\n"
        
        return report
    
    def acknowledge_alert(self, alert_id: str):
        """
        Acknowledge and remove an alert
        """
        self.current_alerts = [alert for alert in self.current_alerts if alert['id'] != alert_id]
        logger.info(f"Alert {alert_id} acknowledged and removed from current alerts")
    
    def get_historical_trends(self, days: int = 30) -> Dict:
        """
        Get historical risk trends
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_alerts = [a for a in self.alert_history if a['timestamp'] >= cutoff_date]
        
        trends = {
            'total_alerts': len(recent_alerts),
            'by_severity': {
                'high': len([a for a in recent_alerts if a['severity'] == 'high']),
                'medium': len([a for a in recent_alerts if a['severity'] == 'medium']),
                'low': len([a for a in recent_alerts if a['severity'] == 'low'])
            },
            'by_type': {},
            'daily_trend': {}  # Alerts per day
        }
        
        # Count by type
        for alert in recent_alerts:
            alert_type = alert['type']
            if alert_type not in trends['by_type']:
                trends['by_type'][alert_type] = 0
            trends['by_type'][alert_type] += 1
        
        # Count by day
        for alert in recent_alerts:
            date_str = alert['timestamp'].date().isoformat()
            if date_str not in trends['daily_trend']:
                trends['daily_trend'][date_str] = 0
            trends['daily_trend'][date_str] += 1
        
        return trends