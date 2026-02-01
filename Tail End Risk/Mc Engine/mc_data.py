"""Data download and price management"""
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

def download_data(stock_symbol, benchmark_symbol, historical_window):
    """Download historical price data from yfinance"""
    print("\nDownloading historical data...")
    # Don't specify end_date - let yfinance use most recent available data
    # Calculate start date from historical window
    calendar_days = int(historical_window * (365/252)) + 100
    start_date = date.today() - timedelta(days=calendar_days)
    
    # Only pass start, let yfinance figure out the end
    stock_data = yf.download(stock_symbol, start=start_date, progress=False, auto_adjust=True)
    benchmark_data = yf.download(benchmark_symbol, start=start_date, progress=False, auto_adjust=True)
    
    if len(stock_data) == 0:
        raise ValueError(f"No data found for {stock_symbol}")
    if len(benchmark_data) == 0:
        raise ValueError(f"No data found for {benchmark_symbol}")
    
    # Flatten multi-level columns if present
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    if isinstance(benchmark_data.columns, pd.MultiIndex):
        benchmark_data.columns = benchmark_data.columns.get_level_values(0)
    
    return stock_data, benchmark_data

def set_starting_prices(stock_data, benchmark_data, stock_symbol, benchmark_symbol, 
                       custom_stock_price=None, custom_benchmark_price=None):
    """Set starting prices from custom values or current market prices"""
    print("\nSetting starting prices...")
    
    if custom_stock_price is not None:
        stock_price = custom_stock_price
        print(f"  Using custom {stock_symbol} price: ${custom_stock_price:.2f}")
    else:
        close_value = stock_data['Close'].iloc[-1]
        stock_price = float(close_value.item() if hasattr(close_value, 'item') else close_value)
        print(f"  Using current {stock_symbol} price: ${stock_price:.2f}")
    
    if custom_benchmark_price is not None:
        benchmark_price = custom_benchmark_price
        print(f"  Using custom {benchmark_symbol} price: ${custom_benchmark_price:.2f}")
    else:
        close_value = benchmark_data['Close'].iloc[-1]
        benchmark_price = float(close_value.item() if hasattr(close_value, 'item') else close_value)
        print(f"  Using current {benchmark_symbol} price: ${benchmark_price:.2f}")
    
    return stock_price, benchmark_price