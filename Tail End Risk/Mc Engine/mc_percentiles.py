"""Percentile calculations"""
import numpy as np
import pandas as pd

def calculate_percentiles(stock_final_returns, benchmark_final_returns, 
                         stock_final_prices=None, benchmark_final_prices=None):
    """Calculate percentile statistics"""
    print("\nCalculating percentiles...")
    
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    
    stock_percentiles = pd.DataFrame({
        'percentile': percentiles,
        'return': np.percentile(stock_final_returns, percentiles)
    })
    
    benchmark_percentiles = pd.DataFrame({
        'percentile': percentiles,
        'return': np.percentile(benchmark_final_returns, percentiles)
    })
    
    # Add price percentiles if prices are provided
    if stock_final_prices is not None:
        stock_percentiles['price'] = np.percentile(stock_final_prices, percentiles)
    if benchmark_final_prices is not None:
        benchmark_percentiles['price'] = np.percentile(benchmark_final_prices, percentiles)
    
    return stock_percentiles, benchmark_percentiles

def calculate_cvar(returns, confidence_level=0.95):
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall
    
    CVaR answers: "If I'm in the worst X% of outcomes, what's my average loss?"
    More conservative than VaR because it captures tail risk beyond the threshold.
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level (0.95 = 95% confidence, looks at worst 5%)
    
    Returns:
        dict: CVaR metrics at different confidence levels
    """
    # Calculate VaR (Value at Risk) thresholds
    var_95 = np.percentile(returns, 5)   # 95% confidence (worst 5%)
    var_99 = np.percentile(returns, 1)   # 99% confidence (worst 1%)
    
    # Calculate CVaR (average of all returns at or below VaR threshold)
    cvar_95 = returns[returns <= var_95].mean()
    cvar_99 = returns[returns <= var_99].mean()
    
    return {
        'var_95': var_95,           # 5th percentile
        'cvar_95': cvar_95,         # Average loss in worst 5%
        'var_99': var_99,           # 1st percentile
        'cvar_99': cvar_99          # Average loss in worst 1%
    }