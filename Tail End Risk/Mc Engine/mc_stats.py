"""Statistics calculations"""
import numpy as np
import pandas as pd

def calculate_statistics(stock_data, benchmark_data, historical_window, stock_symbol, benchmark_symbol):
    """Calculate volatility, correlation, and beta"""
    print("\nCalculating volatility and correlation...")
    
    stock_prices = stock_data['Close'].iloc[-historical_window:]
    benchmark_prices = benchmark_data['Close'].iloc[-historical_window:]
    
    stock_returns = stock_prices.pct_change().dropna()
    benchmark_returns = benchmark_prices.pct_change().dropna()
    
    aligned = pd.DataFrame({
        'stock': stock_returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    stock_volatility = aligned['stock'].std() * np.sqrt(252)
    benchmark_volatility = aligned['benchmark'].std() * np.sqrt(252)
    correlation = aligned['stock'].corr(aligned['benchmark'])
    
    covariance = aligned['stock'].cov(aligned['benchmark'])
    benchmark_variance = aligned['benchmark'].var()
    beta = covariance / benchmark_variance
    
    stock_expected_return = aligned['stock'].mean() * 252
    benchmark_expected_return = aligned['benchmark'].mean() * 252
    
    print(f"  {stock_symbol} volatility: {stock_volatility*100:.2f}%")
    print(f"  {benchmark_symbol} volatility: {benchmark_volatility*100:.2f}%")
    print(f"  Correlation: {correlation:.3f}")
    print(f"  Beta: {beta:.3f}")
    
    return {
        'stock_volatility': stock_volatility,
        'benchmark_volatility': benchmark_volatility,
        'correlation': correlation,
        'beta': beta,
        'stock_expected_return': stock_expected_return,
        'benchmark_expected_return': benchmark_expected_return
    }