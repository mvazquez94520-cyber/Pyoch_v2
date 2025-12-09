#!/usr/bin/env python3
"""
Dashboard Module for MoneyPioch
Creates visualizations and interactive dashboards
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging
from typing import Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class Dashboard:
    """
    Main dashboard class that creates visualizations and reports
    """
    
    def __init__(self):
        """
        Initialize the dashboard system
        """
        self.figures = {}
        self.reports = {}
    
    def update(self, predictions: Dict, recommendations: Dict):
        """
        Update dashboard with latest predictions and recommendations
        """
        logger.info("Updating dashboard with latest data...")
        
        # Create various visualizations
        self.create_match_predictions_chart(predictions)
        self.create_player_performance_chart(predictions)
        self.create_betting_opportunities_chart(recommendations)
        self.create_team_analysis_chart(predictions)
        self.create_risk_heatmap(recommendations)
        
        logger.info("Dashboard updated successfully")
    
    def create_match_predictions_chart(self, predictions: Dict):
        """
        Create chart showing match predictions
        """
        logger.info("Creating match predictions chart...")
        
        match_preds = predictions.get('match_predictions', [])
        
        if not match_preds:
            logger.warning("No match predictions to visualize")
            return
        
        # Prepare data for visualization
        matches = []
        home_probs = []
        draw_probs = []
        away_probs = []
        confidences = []
        
        for pred in match_preds:
            matches.append(f"{pred['home_team']} vs {pred['away_team']}")
            home_probs.append(pred['home_win_probability'])
            draw_probs.append(pred['draw_probability'])
            away_probs.append(pred['away_win_probability'])
            confidences.append(pred['confidence'])
        
        # Create stacked bar chart
        fig = go.Figure(data=[
            go.Bar(name='Home Win', x=matches, y=home_probs, marker_color='blue', opacity=0.7),
            go.Bar(name='Draw', x=matches, y=draw_probs, marker_color='gray', opacity=0.7),
            go.Bar(name='Away Win', x=matches, y=away_probs, marker_color='red', opacity=0.7)
        ])
        
        fig.update_layout(
            title='Match Outcome Probabilities',
            xaxis_title='Matches',
            yaxis_title='Probability',
            barmode='stack',
            height=500
        )
        
        self.figures['match_predictions'] = fig
    
    def create_player_performance_chart(self, predictions: Dict):
        """
        Create chart showing predicted player performance
        """
        logger.info("Creating player performance chart...")
        
        player_preds = predictions.get('player_predictions', [])
        
        if not player_preds:
            logger.warning("No player predictions to visualize")
            return
        
        # Prepare data
        player_names = []
        predicted_ratings = []
        injury_risks = []
        positions = []
        
        for pred in player_preds:
            player_names.append(pred['player_name'])
            predicted_ratings.append(pred['predicted_rating'])
            injury_risks.append(pred['injury_risk'])
            positions.append(pred['position'])
        
        # Create scatter plot
        fig = go.Figure()
        
        # Color by position
        pos_colors = {'Forward': 'red', 'Midfielder': 'green', 'Defender': 'blue', 'Goalkeeper': 'orange'}
        
        for pos in set(positions):
            mask = [i for i, p in enumerate(positions) if p == pos]
            if mask:
                fig.add_trace(go.Scatter(
                    x=[predicted_ratings[i] for i in mask],
                    y=[injury_risks[i] for i in mask],
                    mode='markers',
                    name=pos,
                    text=[player_names[i] for i in mask],
                    marker=dict(
                        size=10,
                        color=pos_colors.get(pos, 'black'),
                        opacity=0.7
                    )
                ))
        
        fig.update_layout(
            title='Player Performance vs Injury Risk',
            xaxis_title='Predicted Rating',
            yaxis_title='Injury Risk',
            height=500
        )
        
        self.figures['player_performance'] = fig
    
    def create_betting_opportunities_chart(self, recommendations: Dict):
        """
        Create chart showing betting opportunities
        """
        logger.info("Creating betting opportunities chart...")
        
        betting_recs = recommendations.get('betting', [])
        
        if not betting_recs:
            logger.warning("No betting recommendations to visualize")
            return
        
        # Prepare data
        matches = []
        expected_values = []
        stakes = []
        confidence_levels = []
        
        for rec in betting_recs:
            matches.append(f"{rec['home_team']} vs {rec['away_team']}")
            expected_values.append(rec['expected_value'])
            stakes.append(rec['stake_suggestion'])
            confidence_levels.append(rec['confidence'])
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Expected Value', 'Recommended Stake (%)'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Bar(x=matches, y=expected_values, name='Expected Value', marker_color='purple'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=matches, y=stakes, name='Stake %', marker_color='orange'),
            row=2, col=1
        )
        
        fig.update_layout(height=600, title_text="Betting Opportunities Analysis")
        
        self.figures['betting_opportunities'] = fig
    
    def create_team_analysis_chart(self, predictions: Dict):
        """
        Create chart analyzing team performance
        """
        logger.info("Creating team analysis chart...")
        
        # For this example, we'll create a simple team strength comparison
        teams_data = {}
        
        # Extract team data from match predictions
        match_preds = predictions.get('match_predictions', [])
        
        for pred in match_preds:
            home_team = pred['home_team']
            away_team = pred['away_team']
            
            if home_team not in teams_data:
                teams_data[home_team] = {'strength': 0, 'count': 0}
            if away_team not in teams_data:
                teams_data[away_team] = {'strength': 0, 'count': 0}
            
            # Use confidence as a measure of team strength for this visualization
            teams_data[home_team]['strength'] += pred['confidence']
            teams_data[home_team]['count'] += 1
            teams_data[away_team]['strength'] += pred['confidence']
            teams_data[away_team]['count'] += 1
        
        # Calculate average strength
        teams = []
        avg_strengths = []
        
        for team, data in teams_data.items():
            if data['count'] > 0:
                teams.append(team)
                avg_strengths.append(data['strength'] / data['count'])
        
        # Create bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=teams,
            y=avg_strengths,
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Team Strength Analysis (Based on Match Prediction Confidence)',
            xaxis_title='Teams',
            yaxis_title='Average Strength Score',
            height=500
        )
        
        self.figures['team_analysis'] = fig
    
    def create_risk_heatmap(self, recommendations: Dict):
        """
        Create heatmap showing various risk factors
        """
        logger.info("Creating risk heatmap...")
        
        risk_alerts = recommendations.get('risk_alerts', [])
        
        if not risk_alerts:
            logger.warning("No risk alerts to visualize")
            # Create a sample heatmap anyway
            categories = ['Betting Risk', 'Injury Concern', 'Prediction Uncertainty']
            severities = ['Low', 'Medium', 'High']
            
            z_data = [[0.2, 0.1, 0.05], [0.15, 0.3, 0.1], [0.1, 0.2, 0.25]]
            
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=severities,
                y=categories,
                colorscale='Reds',
                text=np.array(z_data),
                texttemplate="%{text}",
                textfont={"size": 16},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='Risk Assessment Heatmap',
                height=400
            )
        else:
            # Count risks by type and severity
            risk_matrix = {}
            for alert in risk_alerts:
                r_type = alert['type']
                severity = alert['severity']
                
                if r_type not in risk_matrix:
                    risk_matrix[r_type] = {'low': 0, 'medium': 0, 'high': 0}
                
                risk_matrix[r_type][severity] += 1
            
            # Create heatmap data
            categories = list(risk_matrix.keys())
            severities = ['low', 'medium', 'high']
            
            z_data = []
            for category in categories:
                row = [risk_matrix[category][s] for s in severities]
                z_data.append(row)
            
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=severities,
                y=categories,
                colorscale='Reds',
                text=z_data,
                texttemplate="%{text}",
                textfont={"size": 16},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='Risk Assessment Heatmap',
                height=400
            )
        
        self.figures['risk_heatmap'] = fig
    
    def generate_report(self, predictions: Dict, recommendations: Dict) -> str:
        """
        Generate a comprehensive report from the data
        """
        logger.info("Generating comprehensive report...")
        
        report = f"""
# MoneyPioch Sports Analytics Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- Total Matches Analyzed: {len(predictions.get('match_predictions', []))}
- Total Players Evaluated: {len(predictions.get('player_predictions', []))}
- Betting Recommendations: {len(recommendations.get('betting', []))}
- Risk Alerts Generated: {len(recommendations.get('risk_alerts', []))}

## Top Betting Opportunities
"""
        
        # Add top betting recommendations
        betting_recs = recommendations.get('betting', [])
        for i, rec in enumerate(betting_recs[:5]):  # Top 5
            report += f"- {rec['home_team']} vs {rec['away_team']}: Bet on {rec['bet_on'].upper()} "
            report += f"(EV: {rec['expected_value']:.3f}, Confidence: {rec['confidence']:.2f}, Stake: {rec['stake_suggestion']}%)\n"
        
        report += "\n## Top Team Recommendations\n"
        
        # Add team recommendations
        team_recs = recommendations.get('team_selection', [])
        for rec in team_recs[:3]:  # Top 3 teams
            report += f"- {rec['team']}: Formation {rec['formation']}\n"
            report += f"  Key Players: {[p['name'] for p in rec['key_players']]}\n"
            report += f"  Tactical Advice: {rec['tactical_adjustments']}\n\n"
        
        report += "\n## High-Potential Recruitment Targets\n"
        
        # Add recruitment recommendations
        rec_recs = recommendations.get('recruitment', [])
        for i, rec in enumerate(rec_recs[:5]):  # Top 5
            report += f"- {rec['player_name']} ({rec['position']}) - Current: {rec['current_rating']:.2f}, Potential: {rec['potential_rating']:.2f}\n"
            report += f"  Team: {rec['team_current']}, Priority: {rec['recruitment_priority']}, Value: {rec['estimated_value']}\n"
        
        report += "\n## Risk Assessment Summary\n"
        
        # Add risk summary
        risk_alerts = recommendations.get('risk_alerts', [])
        high_risks = [a for a in risk_alerts if a['severity'] == 'high']
        medium_risks = [a for a in risk_alerts if a['severity'] == 'medium']
        
        report += f"- High Risk Alerts: {len(high_risks)}\n"
        report += f"- Medium Risk Alerts: {len(medium_risks)}\n"
        report += f"- Low Risk Alerts: {len(risk_alerts) - len(high_risks) - len(medium_risks)}\n"
        
        if high_risks:
            report += "\nHigh Risk Details:\n"
            for alert in high_risks[:3]:  # First 3 high risks
                report += f"  - {alert['message']}: {alert['details']}\n"
        
        self.reports['executive_summary'] = report
        return report
    
    def save_visualizations(self, filepath: str = "dashboard_output.html"):
        """
        Save all visualizations to an HTML file
        """
        logger.info(f"Saving visualizations to {filepath}...")
        
        with open(filepath, 'w') as f:
            f.write("<html><head><title>MoneyPioch Dashboard</title></head><body>")
            f.write("<h1>MoneyPioch Sports Analytics Dashboard</h1>")
            
            for name, fig in self.figures.items():
                f.write(f"<h2>{name.replace('_', ' ').title()}</h2>")
                f.write(fig.to_html(include_plotlyjs='cdn'))
            
            f.write("</body></html>")
        
        logger.info(f"Visualizations saved to {filepath}")