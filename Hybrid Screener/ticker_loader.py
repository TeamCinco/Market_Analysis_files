"""Load tickers from JSON file"""
import json
from pathlib import Path

def load_tickers(filepath):
    """
    Load tickers from JSON file
    
    Expected JSON structure:
    {
        "0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
        "1": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
        ...
    }
    
    Also supports simple list format:
    ["AAPL", "MSFT", "GOOGL", ...]
    
    Returns list of ticker symbols
    """
    tickers = []
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Handle dictionary format (your structure)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and 'ticker' in value:
                    ticker = value['ticker'].strip().upper()
                    tickers.append(ticker)
                elif isinstance(value, str):
                    # Simple key-value pair
                    ticker = value.strip().upper()
                    tickers.append(ticker)
        
        # Handle list format
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'ticker' in item:
                    ticker = item['ticker'].strip().upper()
                    tickers.append(ticker)
                elif isinstance(item, str):
                    ticker = item.strip().upper()
                    tickers.append(ticker)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickers = []
        for ticker in tickers:
            if ticker not in seen:
                seen.add(ticker)
                unique_tickers.append(ticker)
        
        return unique_tickers
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}")
        print(f"Details: {e}")
        return []
    
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return []
    
    except Exception as e:
        print(f"Error loading tickers: {e}")
        return []


def load_tickers_legacy(filepath):
    """
    LEGACY: Load tickers from tab-separated text file
    Format: ticker\tvolume
    Returns list of ticker symbols
    
    This is kept for backward compatibility
    """
    tickers = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('\t')
                    if parts:
                        ticker = parts[0].strip().upper()
                        tickers.append(ticker)
        
        return tickers
        
    except Exception as e:
        print(f"Error loading legacy ticker file: {e}")
        return []