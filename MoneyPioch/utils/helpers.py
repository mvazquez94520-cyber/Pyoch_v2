#!/usr/bin/env python3
"""
Helper Utilities for MoneyPioch
Common utility functions used across the system
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any
import json
import pandas as pd

logger = logging.getLogger(__name__)

def setup_logging(log_file: str = 'money_pioch.log', level: int = logging.INFO):
    """
    Set up logging configuration for the application
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from JSON file
    """
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Return default configuration
        return {
            'api_keys': {},
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'money_pioch'
            },
            'betting': {
                'max_stake_percentage': 5.0,
                'min_confidence': 0.65,
                'max_exposure': 10.0
            }
        }

def save_data_to_file(data: Any, filename: str, data_format: str = 'json'):
    """
    Save data to file in specified format
    """
    if data_format == 'json':
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    elif data_format == 'csv':
        if isinstance(data, pd.DataFrame):
            data.to_csv(filename, index=False)
        else:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
    else:
        raise ValueError(f"Unsupported format: {data_format}")
    
    logger.info(f"Data saved to {filename}")

def load_data_from_file(filename: str, data_format: str = None):
    """
    Load data from file
    """
    if data_format is None:
        # Infer format from extension
        if filename.endswith('.json'):
            data_format = 'json'
        elif filename.endswith('.csv'):
            data_format = 'csv'
        else:
            raise ValueError(f"Cannot infer format for file: {filename}")
    
    if data_format == 'json':
        with open(filename, 'r') as f:
            return json.load(f)
    elif data_format == 'csv':
        return pd.read_csv(filename)
    else:
        raise ValueError(f"Unsupported format: {data_format}")

def calculate_streak(values: list) -> int:
    """
    Calculate the current streak (consecutive positive or negative values)
    """
    if not values:
        return 0
    
    current_streak = 1
    current_sign = 1 if values[0] > 0 else -1
    
    for i in range(1, len(values)):
        sign = 1 if values[i] > 0 else -1
        if sign == current_sign:
            current_streak += 1
        else:
            break
    
    return current_streak

def normalize_odd(odd: float) -> float:
    """
    Normalize odds to probability
    """
    if odd <= 0:
        return 0.0
    return 1.0 / odd

def probability_to_odd(probability: float) -> float:
    """
    Convert probability to decimal odds
    """
    if probability <= 0 or probability >= 1:
        return 0.0
    return 1.0 / probability

def calculate_roi(profit: float, stake: float) -> float:
    """
    Calculate Return on Investment
    """
    if stake == 0:
        return 0.0
    return (profit / stake) * 100

def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format amount as currency
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def create_backup(data: Any, backup_dir: str = 'backups') -> str:
    """
    Create a backup of data with timestamp
    """
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = os.path.join(backup_dir, f'backup_{timestamp}.json')
    
    save_data_to_file(data, backup_filename)
    logger.info(f"Backup created: {backup_filename}")
    
    return backup_filename

def validate_percentage(value: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
    """
    Validate if a value is a valid percentage
    """
    return min_val <= value <= max_val

def calculate_correlation(x: list, y: list) -> float:
    """
    Calculate correlation between two lists
    """
    import numpy as np
    
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    x = np.array(x)
    y = np.array(y)
    
    # Calculate correlation coefficient
    correlation_matrix = np.corrcoef(x, y)
    return correlation_matrix[0, 1]

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero
    """
    if denominator == 0:
        return default
    return numerator / denominator

def get_current_season() -> str:
    """
    Get the current football season (e.g., '2023-2024')
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    if current_month >= 8:  # Season starts in August
        return f"{current_year}-{current_year + 1}"
    else:  # Season continues from previous year
        return f"{current_year - 1}-{current_year}"

def format_odds(decimal_odd: float, format_type: str = 'decimal') -> str:
    """
    Format odds in different formats
    """
    if format_type == 'decimal':
        return f"{decimal_odd:.2f}"
    elif format_type == 'fractional':
        # Convert to fractional odds
        fractional = decimal_odd - 1
        # Simplify fraction (basic implementation)
        numerator = int(fractional * 100)
        denominator = 100
        return f"{numerator}/{denominator}"
    elif format_type == 'american':
        if decimal_odd >= 2.0:
            return f"+{int((decimal_odd - 1) * 100)}"
        else:
            return f"-{int(100 / (decimal_odd - 1))}"
    else:
        return str(decimal_odd)