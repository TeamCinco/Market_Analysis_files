"""Screener engine - runs MC analysis on multiple stocks"""
import sys
from pathlib import Path
import yfinance as yf
from datetime import date, timedelta

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
        
        # Get 52-week high
        try:
            # Get 1 year of data for high calculation
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
            hist_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if len(hist_data) > 0:
                recent_high = float(hist_data['High'].max())
                drop_from_high_pct = ((engine.stock_price - recent_high) / recent_high) * 100
            else:
                recent_high = engine.stock_price
                drop_from_high_pct = 0.0
        except:
            recent_high = engine.stock_price
            drop_from_high_pct = 0.0
        
        # Extract key percentiles only
        p5 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 5]['return'].values[0]
        p10 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 10]['return'].values[0]
        p50 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 50]['return'].values[0]
        
        return {
            'ticker': ticker,
            'current_price': engine.stock_price,
            'recent_high': recent_high,
            'drop_from_high_pct': drop_from_high_pct,
            'volatility': engine.stock_volatility * 100,
            'p5': p5,
            'p10': p10,
            'p50': p50,
            'success': True
        }
        
    except Exception as e:
        return {
            'ticker': ticker,
            'success': False,
            'error': str(e)
        }