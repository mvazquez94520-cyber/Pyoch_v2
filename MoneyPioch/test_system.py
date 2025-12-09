#!/usr/bin/env python3
"""
Test script for MoneyPioch system
Verifies that all components can be imported and run
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.data_collector import DataCollector
from analysis.predictor import Predictor
from analysis.recommender import Recommender
from visualization.dashboard import Dashboard
from alerts.risk_monitor import RiskMonitor
from utils.helpers import setup_logging

def test_system():
    """
    Test that all MoneyPioch components work together
    """
    print("Testing MoneyPioch system components...")
    
    # Setup logging
    setup_logging()
    
    # Test data collector
    print("\n1. Testing Data Collector...")
    collector = DataCollector()
    raw_data = collector.collect_all_data()
    print(f"   Collected data for {len(raw_data.get('matches', []))} matches")
    print(f"   Collected data for {len(raw_data.get('players', []))} players")
    print(f"   Collected data for {len(raw_data.get('teams', []))} teams")
    
    # Test predictor
    print("\n2. Testing Predictor...")
    predictor = Predictor()
    predictions = predictor.analyze_data(raw_data)
    print(f"   Generated {len(predictions.get('match_predictions', []))} match predictions")
    print(f"   Generated {len(predictions.get('player_predictions', []))} player predictions")
    
    # Test recommender
    print("\n3. Testing Recommender...")
    recommender = Recommender()
    recommendations = recommender.generate_recommendations(predictions)
    print(f"   Generated {len(recommendations.get('betting', []))} betting recommendations")
    print(f"   Generated {len(recommendations.get('team_selection', []))} team recommendations")
    print(f"   Generated {len(recommendations.get('recruitment', []))} recruitment recommendations")
    
    # Test dashboard
    print("\n4. Testing Dashboard...")
    dashboard = Dashboard()
    dashboard.update(predictions, recommendations)
    print(f"   Created {len(dashboard.figures)} visualizations")
    
    # Generate report
    report = dashboard.generate_report(predictions, recommendations)
    print("   Generated executive summary report")
    
    # Test risk monitor
    print("\n5. Testing Risk Monitor...")
    risk_monitor = RiskMonitor()
    alerts = risk_monitor.check_for_risks(predictions)
    print(f"   Generated {len(alerts)} risk alerts")
    
    # Generate risk report
    risk_report = risk_monitor.generate_risk_report()
    print("   Generated risk report")
    
    print("\n6. System test completed successfully!")
    print("\nMoneyPioch system is ready for use.")
    
    # Display summary
    print(f"\n--- SYSTEM SUMMARY ---")
    print(f"Matches analyzed: {len(raw_data.get('matches', []))}")
    print(f"Players evaluated: {len(raw_data.get('players', []))}")
    print(f"Predictions generated: {len(predictions.get('match_predictions', []))}")
    print(f"Betting opportunities: {len(recommendations.get('betting', []))}")
    print(f"Risk alerts: {len(alerts)}")
    
    return True

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n✓ All tests passed! MoneyPioch system is functioning correctly.")
    else:
        print("\n✗ Tests failed! Check the implementation.")
        sys.exit(1)