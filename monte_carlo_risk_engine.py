"""
Monte Carlo Risk Analysis Engine

This file contains ONLY the engine class.
All parameters are set in run_analysis.py
"""

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path


class MonteCarloRiskEngine:
    """
    Monte Carlo Risk Analysis Engine
    
    Use run_analysis.py to configure parameters and run analysis.
    This class only contains the calculation and visualization logic.
    """
    
    def __init__(
        self,
        stock_symbol,
        benchmark_symbol,
        starting_capital,
        days_to_simulate,
        num_simulations,
        historical_window,
        max_tolerable_loss_pct,
        custom_stock_price=None,
        custom_benchmark_price=None
    ):
        """
        Initialize Monte Carlo Risk Analysis Engine
        
        All parameters are passed from run_analysis.py - NO defaults here
        """
        self.stock_symbol = stock_symbol
        self.benchmark_symbol = benchmark_symbol
        self.starting_capital = starting_capital
        self.days_to_simulate = days_to_simulate
        self.num_simulations = num_simulations
        self.historical_window = historical_window
        self.max_tolerable_loss_pct = max_tolerable_loss_pct
        self.custom_stock_price = custom_stock_price
        self.custom_benchmark_price = custom_benchmark_price
        
        # Download historical data
        print("\nDownloading historical data...")
        self._download_data()
        
        # Set starting prices
        print("\nSetting starting prices...")
        self._set_starting_prices()
        
        # Calculate statistics
        print("\nCalculating volatility and correlation...")
        self._calculate_statistics()
        
        # Run simulations
        print(f"\nRunning {num_simulations:,} Monte Carlo simulations...")
        self._run_monte_carlo()
        
        # Calculate percentiles
        print("\nCalculating percentiles...")
        self._calculate_percentiles()
        
        print("\n✓ Initialization complete!")
    
    def _download_data(self):
        """Download historical price data from yfinance"""
        end_date = datetime.now()
        # Convert trading days to calendar days (252 trading days ≈ 365 calendar days)
        # Add extra buffer to ensure we have enough data
        calendar_days = int(self.historical_window * (365/252)) + 100
        start_date = end_date - timedelta(days=calendar_days)
        
        self.stock_data = yf.download(
            self.stock_symbol,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True
        )
        
        self.benchmark_data = yf.download(
            self.benchmark_symbol,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True
        )
        
        # Verify data exists
        if len(self.stock_data) == 0:
            raise ValueError(f"No data found for {self.stock_symbol}")
        if len(self.benchmark_data) == 0:
            raise ValueError(f"No data found for {self.benchmark_symbol}")
        
        # Flatten multi-level columns if present (yfinance quirk)
        if isinstance(self.stock_data.columns, pd.MultiIndex):
            self.stock_data.columns = self.stock_data.columns.get_level_values(0)
        if isinstance(self.benchmark_data.columns, pd.MultiIndex):
            self.benchmark_data.columns = self.benchmark_data.columns.get_level_values(0)
    
    def _set_starting_prices(self):
        """Set starting prices from custom values or current market prices"""
        if self.custom_stock_price is not None:
            self.stock_price = self.custom_stock_price
            print(f"  Using custom {self.stock_symbol} price: ${self.custom_stock_price:.2f}")
        else:
            # Extract scalar value properly (handles yfinance Series/scalar quirk)
            close_value = self.stock_data['Close'].iloc[-1]
            self.stock_price = float(close_value.item() if hasattr(close_value, 'item') else close_value)
            print(f"  Using current {self.stock_symbol} price: ${self.stock_price:.2f}")
        
        if self.custom_benchmark_price is not None:
            self.benchmark_price = self.custom_benchmark_price
            print(f"  Using custom {self.benchmark_symbol} price: ${self.custom_benchmark_price:.2f}")
        else:
            # Extract scalar value properly
            close_value = self.benchmark_data['Close'].iloc[-1]
            self.benchmark_price = float(close_value.item() if hasattr(close_value, 'item') else close_value)
            print(f"  Using current {self.benchmark_symbol} price: ${self.benchmark_price:.2f}")
    
    def _calculate_statistics(self):
        """Calculate volatility, correlation, and beta"""
        # Use most recent data for statistics
        stock_prices = self.stock_data['Close'].iloc[-self.historical_window:]
        benchmark_prices = self.benchmark_data['Close'].iloc[-self.historical_window:]
        
        # Calculate returns
        stock_returns = stock_prices.pct_change().dropna()
        benchmark_returns = benchmark_prices.pct_change().dropna()
        
        # Align returns
        aligned = pd.DataFrame({
            'stock': stock_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        # Volatility (annualized)
        self.stock_volatility = aligned['stock'].std() * np.sqrt(252)
        self.benchmark_volatility = aligned['benchmark'].std() * np.sqrt(252)
        
        # Correlation
        self.correlation = aligned['stock'].corr(aligned['benchmark'])
        
        # Beta
        covariance = aligned['stock'].cov(aligned['benchmark'])
        benchmark_variance = aligned['benchmark'].var()
        self.beta = covariance / benchmark_variance
        
        # Expected returns (annualized) - using historical mean
        self.stock_expected_return = aligned['stock'].mean() * 252
        self.benchmark_expected_return = aligned['benchmark'].mean() * 252
        
        print(f"  {self.stock_symbol} volatility: {self.stock_volatility*100:.2f}%")
        print(f"  {self.benchmark_symbol} volatility: {self.benchmark_volatility*100:.2f}%")
        print(f"  Correlation: {self.correlation:.3f}")
        print(f"  Beta: {self.beta:.3f}")
    
    def _run_monte_carlo(self):
        """Run Monte Carlo simulations"""
        # Generate correlated random returns
        np.random.seed(42)  # For reproducibility
        
        # Generate independent standard normal variables
        z1 = np.random.standard_normal((self.days_to_simulate, self.num_simulations))
        z2 = np.random.standard_normal((self.days_to_simulate, self.num_simulations))
        
        # Create correlated returns using Cholesky decomposition
        benchmark_daily_returns = (
            self.benchmark_expected_return / 252 +
            self.benchmark_volatility / np.sqrt(252) * z1
        )
        
        stock_daily_returns = (
            self.stock_expected_return / 252 +
            self.stock_volatility / np.sqrt(252) * (
                self.correlation * z1 + np.sqrt(1 - self.correlation**2) * z2
            )
        )
        
        # Generate price paths
        self.stock_paths = self.stock_price * np.cumprod(1 + stock_daily_returns, axis=0)
        self.benchmark_paths = self.benchmark_price * np.cumprod(1 + benchmark_daily_returns, axis=0)
        
        # Store final prices
        self.stock_final_prices = self.stock_paths[-1]
        self.benchmark_final_prices = self.benchmark_paths[-1]
        
        # Calculate returns
        self.stock_final_returns = (self.stock_final_prices / self.stock_price - 1) * 100
        self.benchmark_final_returns = (self.benchmark_final_prices / self.benchmark_price - 1) * 100
    
    def _calculate_percentiles(self):
        """Calculate percentile statistics"""
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        
        self.stock_percentiles = pd.DataFrame({
            'percentile': percentiles,
            'price': np.percentile(self.stock_final_prices, percentiles),
            'return': np.percentile(self.stock_final_returns, percentiles)
        })
        
        self.benchmark_percentiles = pd.DataFrame({
            'percentile': percentiles,
            'price': np.percentile(self.benchmark_final_prices, percentiles),
            'return': np.percentile(self.benchmark_final_returns, percentiles)
        })
    
    def run_full_analysis(self):
        """Run complete analysis and generate visualization"""
        print("\nGenerating visualization...")
        
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Title
        fig.suptitle(
            f'Monte Carlo Risk Analysis: {self.stock_symbol} vs {self.benchmark_symbol}\n'
            f'{self.num_simulations:,} simulations over {self.days_to_simulate} days',
            fontsize=16,
            fontweight='bold'
        )
        
        # 1. Stock price paths
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_price_paths(ax1, self.stock_paths, self.stock_symbol, self.stock_price)
        
        # 2. Benchmark price paths
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_price_paths(ax2, self.benchmark_paths, self.benchmark_symbol, self.benchmark_price)
        
        # 3. Stock return distribution
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_return_distribution(ax3, self.stock_final_returns, self.stock_symbol)
        
        # 4. Benchmark return distribution
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_return_distribution(ax4, self.benchmark_final_returns, self.benchmark_symbol)
        
        # 5. Scatter plot
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_scatter(ax5)
        
        # 6. Rolling correlation
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_rolling_correlation(ax6)
        
        # 7. Percentile comparison table
        ax7 = fig.add_subplot(gs[2, 0])
        self._plot_percentile_table(ax7)
        
        # 8. Position sizing
        ax8 = fig.add_subplot(gs[2, 1])
        self._plot_position_sizing(ax8)
        
        # 9. Statistical summary
        ax9 = fig.add_subplot(gs[2, 2])
        self._plot_statistical_summary(ax9)
        
        # Save figure
        output_dir = Path('/Users/jazzhashzzz/Documents/Market_Analysis_files/output/monte_carlo_risk_engine')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self.custom_stock_price is not None:
            filename = f'monte_carlo_{self.stock_symbol}_BACKTEST_{timestamp}.png'
        else:
            filename = f'monte_carlo_{self.stock_symbol}_{timestamp}.png'
        
        output_path = output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_price_paths(self, ax, paths, symbol, starting_price):
        """Plot price path distribution"""
        # Normalize to starting price = 100
        normalized_paths = (paths / starting_price) * 100
        
        percentiles_to_plot = [5, 25, 50, 75, 95]
        colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
        
        for i, p in enumerate(percentiles_to_plot):
            percentile_path = np.percentile(normalized_paths, p, axis=1)
            ax.plot(percentile_path, label=f'{p}th percentile', color=colors[i], linewidth=2)
        
        ax.fill_between(
            range(self.days_to_simulate),
            np.percentile(normalized_paths, 5, axis=1),
            np.percentile(normalized_paths, 95, axis=1),
            alpha=0.2,
            color='blue',
            label='5th-95th percentile range'
        )
        
        ax.set_xlabel('Trading Days', fontsize=10)
        ax.set_ylabel('Normalized Price (Start = 100)', fontsize=10)
        ax.set_title(f'{symbol} - Price Path Distribution', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_return_distribution(self, ax, returns, symbol):
        """Plot return distribution histogram"""
        ax.hist(returns, bins=100, alpha=0.7, color='blue', edgecolor='black')
        
        # Add percentile lines
        p5 = np.percentile(returns, 5)
        p50 = np.percentile(returns, 50)
        p95 = np.percentile(returns, 95)
        
        ax.axvline(p5, color='red', linestyle='--', linewidth=2, label=f'5th percentile')
        ax.axvline(p50, color='yellow', linestyle='--', linewidth=2, label=f'Median')
        ax.axvline(p95, color='green', linestyle='--', linewidth=2, label=f'95th percentile')
        
        ax.set_xlabel('Return (%)', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'{symbol} - Final Return Distribution', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_scatter(self, ax):
        """Plot stock vs benchmark returns scatter"""
        ax.scatter(
            self.benchmark_final_returns,
            self.stock_final_returns,
            alpha=0.3,
            s=1,
            color='blue'
        )
        
        # Add regression line
        z = np.polyfit(self.benchmark_final_returns, self.stock_final_returns, 1)
        p = np.poly1d(z)
        x_line = np.linspace(self.benchmark_final_returns.min(), self.benchmark_final_returns.max(), 100)
        ax.plot(x_line, p(x_line), "r-", linewidth=2, label=f'Beta = {self.beta:.2f}')
        
        ax.set_xlabel(f'{self.benchmark_symbol} Return (%)', fontsize=10)
        ax.set_ylabel(f'{self.stock_symbol} Return (%)', fontsize=10)
        ax.set_title(f'{self.stock_symbol} vs {self.benchmark_symbol} Returns', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_rolling_correlation(self, ax):
        """Plot 30-day rolling correlation"""
        stock_prices = self.stock_data['Close'].iloc[-self.historical_window:]
        benchmark_prices = self.benchmark_data['Close'].iloc[-self.historical_window:]
        
        stock_returns = stock_prices.pct_change()
        benchmark_returns = benchmark_prices.pct_change()
        
        rolling_corr = stock_returns.rolling(30).corr(benchmark_returns)
        
        ax.plot(rolling_corr.index, rolling_corr.values, color='purple', linewidth=2)
        ax.axhline(y=self.correlation, color='red', linestyle='--', linewidth=2, label=f'Average = {self.correlation:.3f}')
        
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Correlation', fontsize=10)
        ax.set_title('30-Day Rolling Correlation', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    def _plot_percentile_table(self, ax):
        """Plot percentile comparison table"""
        ax.axis('tight')
        ax.axis('off')
        
        table_data = []
        percentiles_to_show = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        
        for p in percentiles_to_show:
            stock_val = self.stock_percentiles[self.stock_percentiles['percentile'] == p]['return'].values[0]
            bench_val = self.benchmark_percentiles[self.benchmark_percentiles['percentile'] == p]['return'].values[0]
            table_data.append([f'{p}th', f'{stock_val:.2f}%', f'{bench_val:.2f}%'])
        
        table = ax.table(
            cellText=table_data,
            colLabels=['Percentile', self.stock_symbol, self.benchmark_symbol],
            cellLoc='center',
            loc='center',
            colWidths=[0.3, 0.35, 0.35]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Color code cells
        for i, row in enumerate(table_data):
            if i < 3:  # 1st, 5th, 10th percentile (downside)
                table[(i+1, 1)].set_facecolor('#ffcccc')
                table[(i+1, 2)].set_facecolor('#ffcccc')
            elif i == 4:  # 50th percentile (median)
                table[(i+1, 1)].set_facecolor('#ffffcc')
                table[(i+1, 2)].set_facecolor('#ffffcc')
            elif i >= 6:  # 90th, 95th, 99th percentile (upside)
                table[(i+1, 1)].set_facecolor('#ccffcc')
                table[(i+1, 2)].set_facecolor('#ccffcc')
        
        # Header styling
        for j in range(3):
            table[(0, j)].set_facecolor('#4CAF50')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Percentile Comparison', fontsize=12, fontweight='bold', pad=20)
    
    def _plot_position_sizing(self, ax):
        """Plot position sizing recommendation"""
        ax.axis('tight')
        ax.axis('off')
        
        # Calculate position sizing
        loss_5th = self.stock_percentiles[self.stock_percentiles['percentile'] == 5]['return'].values[0]
        capital_at_risk = abs(loss_5th) / 100 * self.starting_capital
        max_loss_dollars = self.max_tolerable_loss_pct / 100 * self.starting_capital
        
        if abs(loss_5th) > 0:
            recommended_position = min(max_loss_dollars / abs(loss_5th) * 100, self.starting_capital)
        else:
            recommended_position = self.starting_capital
        
        position_pct = (recommended_position / self.starting_capital) * 100
        cash_pct = 100 - position_pct
        
        table_data = [
            ['Starting Capital', f'${self.starting_capital:,.2f}'],
            ['Max Loss Tolerance', f'{self.max_tolerable_loss_pct}%'],
            ['', ''],
            ['5th Percentile Loss', f'{loss_5th:.2f}%'],
            ['Recommended Position', f'${recommended_position:,.2f}'],
            ['Position %', f'{position_pct:.1f}%'],
            ['Cash %', f'{cash_pct:.1f}%'],
        ]
        
        table = ax.table(
            cellText=table_data,
            cellLoc='left',
            loc='center',
            colWidths=[0.6, 0.4]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        ax.set_title('Position Sizing Recommendation', fontsize=12, fontweight='bold', pad=20)
    
    def _plot_statistical_summary(self, ax):
        """Plot statistical summary"""
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [
            ['', self.stock_symbol, self.benchmark_symbol],
            ['Ann. Return', f'{self.stock_expected_return*100:.2f}%', f'{self.benchmark_expected_return*100:.2f}%'],
            ['Ann. Volatility', f'{self.stock_volatility*100:.2f}%', f'{self.benchmark_volatility*100:.2f}%'],
            ['Correlation', f'{self.correlation:.3f}', '1.000'],
            ['Beta', f'{self.beta:.3f}', '1.000'],
        ]
        
        table = ax.table(
            cellText=table_data,
            cellLoc='center',
            loc='center',
            colWidths=[0.4, 0.3, 0.3]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Header styling
        for j in range(3):
            table[(0, j)].set_facecolor('#4CAF50')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)