"""
Statistical Dislocation Detector
Identifies mean-reversion opportunities using Z-scores
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_z_score_dislocation(ticker, config, sector_etf=None):
    """
    Calculate Z-score based statistical dislocation
    
    Args:
        ticker: Stock symbol
        config: Configuration object
        sector_etf: Sector ETF ticker (for sector-relative mode)
        
    Returns:
        dict with z_score, signal, distance_from_mean, realized_vol, etc.
    """
    try:
        # Download historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(config.HISTORICAL_WINDOW * 1.5))  # Buffer for weekends/holidays
        
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if len(stock_data) < config.ROLLING_WINDOW + 20:
            return {
                'success': False,
                'reason': 'Insufficient data',
                'z_score': None,
                'signal': None
            }
        
        # Calculate returns
        stock_data['returns'] = stock_data['Adj Close'].pct_change()
        
        # Sector-relative mode
        if config.USE_SECTOR_RELATIVE and sector_etf:
            try:
                sector_data = yf.download(sector_etf, start=start_date, end=end_date, progress=False)
                sector_data['returns'] = sector_data['Adj Close'].pct_change()
                
                # Align dates
                aligned = pd.merge(
                    stock_data[['returns']], 
                    sector_data[['returns']], 
                    left_index=True, 
                    right_index=True, 
                    suffixes=('_stock', '_sector')
                )
                
                # Calculate spread
                aligned['spread'] = aligned['returns_stock'] - aligned['returns_sector']
                
                # Use spread for Z-score
                target_series = aligned['spread']
            except:
                # Fallback to absolute if sector fails
                target_series = stock_data['returns']
        else:
            # Absolute mode
            if config.Z_SCORE_METHOD == "returns":
                target_series = stock_data['returns']
            else:  # prices
                target_series = stock_data['Adj Close']
        
        # Calculate rolling statistics
        rolling_mean = target_series.rolling(window=config.ROLLING_WINDOW).mean()
        rolling_std = target_series.rolling(window=config.ROLLING_WINDOW).std()
        
        # Calculate Z-score
        current_value = target_series.iloc[-1]
        current_mean = rolling_mean.iloc[-1]
        current_std = rolling_std.iloc[-1]
        
        if pd.isna(current_std) or current_std == 0:
            return {
                'success': False,
                'reason': 'Invalid std deviation',
                'z_score': None,
                'signal': None
            }
        
        z_score = (current_value - current_mean) / current_std
        
        # Determine signal
        signal = None
        if z_score <= config.Z_SCORE_OVERSOLD:
            signal = 'LONG'  # Mean reversion long
        elif z_score >= config.Z_SCORE_OVERBOUGHT:
            signal = 'SHORT'  # Mean reversion short
        
        # Distance from mean (percentage for prices, basis points for returns)
        if config.Z_SCORE_METHOD == "prices":
            distance_from_mean = ((current_value - current_mean) / current_mean) * 100
        else:
            distance_from_mean = (current_value - current_mean) * 10000  # basis points
        
        # Calculate 20-day realized volatility (annualized)
        realized_vol_20d = stock_data['returns'].tail(20).std() * np.sqrt(252) * 100
        
        # Historical volatility percentile
        vol_series = stock_data['returns'].rolling(window=20).std() * np.sqrt(252) * 100
        vol_percentile = (vol_series < realized_vol_20d).sum() / len(vol_series.dropna()) * 100
        
        # Current price
        current_price = stock_data['Adj Close'].iloc[-1]
        
        return {
            'success': True,
            'z_score': z_score,
            'signal': signal,
            'distance_from_mean': distance_from_mean,
            'realized_vol_20d': realized_vol_20d,
            'vol_percentile': vol_percentile,
            'current_price': current_price,
            'rolling_mean': current_mean,
            'rolling_std': current_std,
            'sector_relative': config.USE_SECTOR_RELATIVE and sector_etf is not None
        }
        
    except Exception as e:
        return {
            'success': False,
            'reason': str(e),
            'z_score': None,
            'signal': None
        }


def check_dislocation_trigger(ticker, config, sector=None):
    """
    Main function to check if stock has statistical dislocation
    
    Returns:
        dict with signal details or None if no signal
    """
    # Get sector ETF if in sector-relative mode
    sector_etf = None
    if config.USE_SECTOR_RELATIVE and sector and sector in config.SECTOR_ETFS:
        sector_etf = config.SECTOR_ETFS[sector]
    
    # Calculate Z-score
    result = calculate_z_score_dislocation(ticker, config, sector_etf)
    
    if not result['success']:
        return None
    
    # Only return if there's a signal
    if result['signal']:
        return result
    
    return None