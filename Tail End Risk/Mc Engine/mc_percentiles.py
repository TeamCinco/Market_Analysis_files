"""Percentile calculations"""
import numpy as np
import pandas as pd

def calculate_percentiles(stock_final_returns, benchmark_final_returns):
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
    
    return stock_percentiles, benchmark_percentiles