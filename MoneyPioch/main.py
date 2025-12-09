#!/usr/bin/env python3
"""
MoneyPioch - Advanced Sports Analytics and Betting Optimization System
Main application entry point
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('money_pioch.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for MoneyPioch system
    """
    logger.info("Starting MoneyPioch - Sports Analytics and Betting Optimization System")
    logger.info(f"System initialized at {datetime.now()}")
    
    # Import and initialize core components
    try:
        from api.data_collector import DataCollector
        from analysis.predictor import Predictor
        from analysis.recommender import Recommender
        from visualization.dashboard import Dashboard
        from alerts.risk_monitor import RiskMonitor
        
        # Initialize core components
        collector = DataCollector()
        predictor = Predictor()
        recommender = Recommender()
        dashboard = Dashboard()
        risk_monitor = RiskMonitor()
        
        logger.info("All components initialized successfully")
        
        # Run the main system loop
        while True:
            try:
                # Collect latest data
                logger.info("Collecting latest sports data...")
                sports_data = collector.collect_all_data()
                
                # Analyze and predict
                logger.info("Analyzing data and generating predictions...")
                predictions = predictor.analyze_data(sports_data)
                
                # Generate recommendations
                logger.info("Generating recommendations...")
                recommendations = recommender.generate_recommendations(predictions)
                
                # Update dashboard
                logger.info("Updating dashboard...")
                dashboard.update(predictions, recommendations)
                
                # Check for risks and alerts
                logger.info("Checking for risks and alerts...")
                alerts = risk_monitor.check_for_risks(predictions)
                
                logger.info("System cycle completed successfully")
                
                # For now, we'll just run once instead of infinite loop
                break
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                break
                
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        sys.exit(1)
    
    logger.info("MoneyPioch system completed execution")

if __name__ == "__main__":
    main()