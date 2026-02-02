"""Screener engine - runs MC analysis on multiple stocks"""
import sys
from pathlib import Path

# Add Mc Engine to path
mc_engine_path = Path("/Users/jazzhashzzz/Documents/Market_Analysis_files/Tail End Risk/Mc Engine")
sys.path.insert(0, str(mc_engine_path))

from monte_carlo_risk_engine import MonteCarloRiskEngine
import warnings
warnings.filterwarnings('ignore')

def analyze_stock(ticker, days_to_simulate=90, num_simulations=10000, historical_window=252*6):
    """
    Run Monte Carlo analysis on a single stock
    Returns dict with key metrics or None if failed
    """
    try:
        engine = MonteCarloRiskEngine(
            stock_symbol=ticker,
            starting_capital=1000,
            days_to_simulate=days_to_simulate,
            num_simulations=num_simulations,
            historical_window=historical_window,
            max_tolerable_loss_pct=80
        )
        
        # Extract metrics
        percentiles = {}
        for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
            row = engine.stock_percentiles[engine.stock_percentiles['percentile'] == p]
            percentiles[f'p{p}'] = row['return'].values[0]
        
        return {
            'ticker': ticker,
            'current_price': engine.stock_price,
            'volatility': engine.stock_volatility * 100,
            'expected_return': engine.stock_expected_return * 100,
            'var_95': engine.stock_cvar['var_95'],
            'cvar_95': engine.stock_cvar['cvar_95'],
            'var_99': engine.stock_cvar['var_99'],
            'cvar_99': engine.stock_cvar['cvar_99'],
            **percentiles,
            'success': True
        }
        
    except Exception as e:
        return {
            'ticker': ticker,
            'success': False,
            'error': str(e)
        }