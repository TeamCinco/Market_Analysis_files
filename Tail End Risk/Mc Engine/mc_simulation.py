"""Monte Carlo simulation"""
import numpy as np

def run_monte_carlo(stock_price, benchmark_price, stats, days_to_simulate, num_simulations):
    """Run Monte Carlo simulations"""
    print(f"\nRunning {num_simulations:,} Monte Carlo simulations...")
    
    np.random.seed(42)
    
    z1 = np.random.standard_normal((days_to_simulate, num_simulations))
    z2 = np.random.standard_normal((days_to_simulate, num_simulations))
    
    benchmark_daily_returns = (
        stats['benchmark_expected_return'] / 252 +
        stats['benchmark_volatility'] / np.sqrt(252) * z1
    )
    
    stock_daily_returns = (
        stats['stock_expected_return'] / 252 +
        stats['stock_volatility'] / np.sqrt(252) * (
            stats['correlation'] * z1 + np.sqrt(1 - stats['correlation']**2) * z2
        )
    )
    
    stock_paths = stock_price * np.cumprod(1 + stock_daily_returns, axis=0)
    benchmark_paths = benchmark_price * np.cumprod(1 + benchmark_daily_returns, axis=0)
    
    stock_final_prices = stock_paths[-1]
    benchmark_final_prices = benchmark_paths[-1]
    
    stock_final_returns = (stock_final_prices / stock_price - 1) * 100
    benchmark_final_returns = (benchmark_final_prices / benchmark_price - 1) * 100
    
    return {
        'stock_paths': stock_paths,
        'benchmark_paths': benchmark_paths,
        'stock_final_returns': stock_final_returns,
        'benchmark_final_returns': benchmark_final_returns
    }