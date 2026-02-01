"""
Monte Carlo Risk Analysis - DEMO VERSION
Uses synthetic data to demonstrate functionality
(Replace with real data when yfinance works or use CSV import)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MonteCarloRiskEngineDemo:
    """
    Demo version with synthetic data
    """
    
    def __init__(self, 
                 stock_symbol,
                 benchmark_symbol,
                 starting_capital,
                 days_to_simulate=252,
                 num_simulations=25000,
                 max_tolerable_loss_pct=20):
        
        self.stock_symbol = stock_symbol.upper()
        self.benchmark_symbol = benchmark_symbol.upper()
        self.starting_capital = starting_capital
        self.days_to_simulate = days_to_simulate
        self.num_simulations = num_simulations
        self.max_tolerable_loss_pct = max_tolerable_loss_pct
        
        # Generate synthetic data (realistic parameters based on TSLA/SPY)
        print(f"\n{'='*60}")
        print(f"Generating synthetic data for {self.stock_symbol} and {self.benchmark_symbol}...")
        print(f"{'='*60}")
        
        # Synthetic parameters (you can modify these)
        self.stock_mu = 0.15        # 15% annual return
        self.stock_sigma = 0.45     # 45% annual volatility (high like TSLA)
        self.benchmark_mu = 0.10    # 10% annual return
        self.benchmark_sigma = 0.16 # 16% annual volatility (typical SPY)
        self.correlation = 0.65     # 65% correlation
        self.beta = 1.8             # Stock is 1.8x as volatile as benchmark
        
        print(f"\nUsing realistic synthetic parameters:")
        print(f"  {stock_symbol}: 15% return, 45% volatility")
        print(f"  {benchmark_symbol}: 10% return, 16% volatility")
        print(f"  Correlation: 0.65, Beta: 1.8")
        
        self.stock_simulations = None
        self.benchmark_simulations = None
        
    def run_simulation(self):
        """Run correlated Monte Carlo simulation"""
        print(f"\n{'='*60}")
        print(f"Running {self.num_simulations:,} Monte Carlo simulations...")
        print(f"{'='*60}")
        
        dt = 1/252
        
        self.stock_simulations = np.zeros((self.days_to_simulate + 1, self.num_simulations))
        self.benchmark_simulations = np.zeros((self.days_to_simulate + 1, self.num_simulations))
        
        self.stock_simulations[0] = 100
        self.benchmark_simulations[0] = 100
        
        for t in range(1, self.days_to_simulate + 1):
            z1 = np.random.standard_normal(self.num_simulations)
            z2 = np.random.standard_normal(self.num_simulations)
            
            shock_benchmark = z1
            shock_stock = self.correlation * z1 + np.sqrt(1 - self.correlation**2) * z2
            
            self.benchmark_simulations[t] = self.benchmark_simulations[t-1] * np.exp(
                (self.benchmark_mu - 0.5 * self.benchmark_sigma**2) * dt +
                self.benchmark_sigma * np.sqrt(dt) * shock_benchmark
            )
            
            self.stock_simulations[t] = self.stock_simulations[t-1] * np.exp(
                (self.stock_mu - 0.5 * self.stock_sigma**2) * dt +
                self.stock_sigma * np.sqrt(dt) * shock_stock
            )
        
        print(f"✓ Simulation complete")
        
    def calculate_percentiles(self):
        """Calculate percentile outcomes"""
        stock_final = self.stock_simulations[-1]
        benchmark_final = self.benchmark_simulations[-1]
        
        stock_returns_pct = (stock_final / 100 - 1) * 100
        benchmark_returns_pct = (benchmark_final / 100 - 1) * 100
        
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        
        stock_percentiles = np.percentile(stock_returns_pct, percentiles)
        benchmark_percentiles = np.percentile(benchmark_returns_pct, percentiles)
        
        print(f"\n{'='*60}")
        print(f"PERCENTILE ANALYSIS ({self.days_to_simulate} days)")
        print(f"{'='*60}")
        
        print(f"\n{'Percentile':<12} {self.stock_symbol:>12} {self.benchmark_symbol:>12}")
        print(f"{'-'*40}")
        for i, p in enumerate(percentiles):
            print(f"{p}th %ile{'':<6} {stock_percentiles[i]:>11.2f}% {benchmark_percentiles[i]:>11.2f}%")
        
        return stock_percentiles, benchmark_percentiles
    
    def calculate_position_sizing(self):
        """Calculate recommended position size"""
        print(f"\n{'='*60}")
        print("POSITION SIZING ANALYSIS")
        print(f"{'='*60}")
        
        stock_final = self.stock_simulations[-1]
        stock_returns_pct = (stock_final / 100 - 1) * 100
        fifth_percentile_loss = np.percentile(stock_returns_pct, 5)
        
        print(f"\nStarting Capital: ${self.starting_capital:,.2f}")
        print(f"Max Tolerable Loss: {self.max_tolerable_loss_pct}% (${self.starting_capital * self.max_tolerable_loss_pct/100:,.2f})")
        print(f"\n5th Percentile Outcome: {fifth_percentile_loss:.2f}%")
        
        if fifth_percentile_loss < 0:
            max_loss_dollars = self.starting_capital * (self.max_tolerable_loss_pct / 100)
            recommended_position = max_loss_dollars / (abs(fifth_percentile_loss) / 100)
            recommended_position = min(recommended_position, self.starting_capital)
            
            position_pct = (recommended_position / self.starting_capital) * 100
            
            print(f"\n{'='*60}")
            print("RECOMMENDATION:")
            print(f"{'='*60}")
            print(f"Recommended Position: ${recommended_position:,.2f} ({position_pct:.1f}% of capital)")
            print(f"\nIf 5th percentile occurs:")
            print(f"  Loss = ${recommended_position * abs(fifth_percentile_loss)/100:,.2f}")
            
            if recommended_position < self.starting_capital:
                print(f"\n⚠️  WARNING: Stock is too volatile for full capital allocation")
                print(f"   Keep ${self.starting_capital - recommended_position:,.2f} in cash")
            else:
                print(f"\n✓ Full capital allocation is within risk tolerance")
        else:
            print(f"\n✓ Even 5th percentile shows positive return - low downside risk")
    
    def analyze_regimes(self):
        """Analyze performance under different volatility regimes"""
        print(f"\n{'='*60}")
        print("REGIME ANALYSIS")
        print(f"{'='*60}")
        
        vol_low = self.stock_sigma * 0.7    # 70% of normal vol
        vol_medium = self.stock_sigma       # Normal vol
        vol_high = self.stock_sigma * 1.5   # 150% of normal vol
        
        print(f"\nVolatility Regimes for {self.stock_symbol}:")
        print(f"  LOW VOL:    {vol_low*100:.2f}%")
        print(f"  MEDIUM VOL: {vol_medium*100:.2f}%")
        print(f"  HIGH VOL:   {vol_high*100:.2f}%")
        
        regimes = {
            'LOW VOL': vol_low,
            'MEDIUM VOL': vol_medium,
            'HIGH VOL': vol_high
        }
        
        print(f"\n{'Regime':<15} {'5th %ile':<12} {'50th %ile':<12} {'95th %ile':<12}")
        print(f"{'-'*55}")
        
        for regime_name, regime_vol in regimes.items():
            temp_simulations = np.zeros((self.days_to_simulate + 1, 5000))
            temp_simulations[0] = 100
            dt = 1/252
            
            for t in range(1, self.days_to_simulate + 1):
                shock = np.random.standard_normal(5000)
                temp_simulations[t] = temp_simulations[t-1] * np.exp(
                    (self.stock_mu - 0.5 * regime_vol**2) * dt +
                    regime_vol * np.sqrt(dt) * shock
                )
            
            final_returns = (temp_simulations[-1] / 100 - 1) * 100
            p5 = np.percentile(final_returns, 5)
            p50 = np.percentile(final_returns, 50)
            p95 = np.percentile(final_returns, 95)
            
            print(f"{regime_name:<15} {p5:>10.2f}% {p50:>10.2f}% {p95:>10.2f}%")
        
    def plot_results(self):
        """Generate visualizations"""
        print(f"\n{'='*60}")
        print("Generating visualizations...")
        print(f"{'='*60}")
        
        fig = plt.figure(figsize=(20, 12))
        
        # 1. Stock Price Paths
        ax1 = plt.subplot(3, 3, 1)
        percentiles_to_plot = [5, 25, 50, 75, 95]
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(percentiles_to_plot)))
        
        for i, p in enumerate(percentiles_to_plot):
            path = np.percentile(self.stock_simulations, p, axis=1)
            ax1.plot(path, label=f'{p}th percentile', color=colors[i], linewidth=2)
        
        ax1.fill_between(range(self.days_to_simulate + 1),
                         np.percentile(self.stock_simulations, 5, axis=1),
                         np.percentile(self.stock_simulations, 95, axis=1),
                         alpha=0.2, color='blue')
        ax1.set_title(f'{self.stock_symbol} - Price Path Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Trading Days')
        ax1.set_ylabel('Normalized Price (Start = 100)')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. Benchmark Price Paths
        ax2 = plt.subplot(3, 3, 2)
        for i, p in enumerate(percentiles_to_plot):
            path = np.percentile(self.benchmark_simulations, p, axis=1)
            ax2.plot(path, label=f'{p}th percentile', color=colors[i], linewidth=2)
        
        ax2.fill_between(range(self.days_to_simulate + 1),
                         np.percentile(self.benchmark_simulations, 5, axis=1),
                         np.percentile(self.benchmark_simulations, 95, axis=1),
                         alpha=0.2, color='green')
        ax2.set_title(f'{self.benchmark_symbol} - Price Path Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Trading Days')
        ax2.set_ylabel('Normalized Price (Start = 100)')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Stock Final Return Distribution
        ax3 = plt.subplot(3, 3, 3)
        stock_final_returns = (self.stock_simulations[-1] / 100 - 1) * 100
        ax3.hist(stock_final_returns, bins=100, alpha=0.7, color='blue', edgecolor='black')
        ax3.axvline(np.percentile(stock_final_returns, 5), color='red', linestyle='--', 
                   linewidth=2, label='5th percentile')
        ax3.axvline(np.percentile(stock_final_returns, 50), color='yellow', linestyle='--', 
                   linewidth=2, label='Median')
        ax3.axvline(np.percentile(stock_final_returns, 95), color='green', linestyle='--', 
                   linewidth=2, label='95th percentile')
        ax3.set_title(f'{self.stock_symbol} - Final Return Distribution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Return (%)')
        ax3.set_ylabel('Frequency')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. Benchmark Final Return Distribution
        ax4 = plt.subplot(3, 3, 4)
        benchmark_final_returns = (self.benchmark_simulations[-1] / 100 - 1) * 100
        ax4.hist(benchmark_final_returns, bins=100, alpha=0.7, color='green', edgecolor='black')
        ax4.axvline(np.percentile(benchmark_final_returns, 5), color='red', linestyle='--', 
                   linewidth=2, label='5th percentile')
        ax4.axvline(np.percentile(benchmark_final_returns, 50), color='yellow', linestyle='--', 
                   linewidth=2, label='Median')
        ax4.axvline(np.percentile(benchmark_final_returns, 95), color='green', linestyle='--', 
                   linewidth=2, label='95th percentile')
        ax4.set_title(f'{self.benchmark_symbol} - Final Return Distribution', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Return (%)')
        ax4.set_ylabel('Frequency')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 5. Stock vs Benchmark Scatter
        ax5 = plt.subplot(3, 3, 5)
        sample_size = 5000
        indices = np.random.choice(self.num_simulations, sample_size, replace=False)
        stock_sample = stock_final_returns[indices]
        benchmark_sample = benchmark_final_returns[indices]
        
        ax5.scatter(benchmark_sample, stock_sample, alpha=0.3, s=10)
        
        z = np.polyfit(benchmark_sample, stock_sample, 1)
        p = np.poly1d(z)
        ax5.plot(benchmark_sample, p(benchmark_sample), "r--", linewidth=2, 
                label=f'Beta = {self.beta:.2f}')
        
        ax5.set_title(f'{self.stock_symbol} vs {self.benchmark_symbol} Returns', fontsize=12, fontweight='bold')
        ax5.set_xlabel(f'{self.benchmark_symbol} Return (%)')
        ax5.set_ylabel(f'{self.stock_symbol} Return (%)')
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3)
        
        # 6. Correlation visualization
        ax6 = plt.subplot(3, 3, 6)
        ax6.text(0.5, 0.5, f'Correlation: {self.correlation:.3f}\n\nThis represents how closely\n{self.stock_symbol} moves with\n{self.benchmark_symbol}',
                ha='center', va='center', fontsize=14, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax6.axis('off')
        ax6.set_title('Stock-Benchmark Relationship', fontsize=12, fontweight='bold')
        
        # 7. Percentile Table
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        stock_pct = np.percentile(stock_final_returns, percentiles)
        bench_pct = np.percentile(benchmark_final_returns, percentiles)
        
        table_data = []
        for i, p in enumerate(percentiles):
            table_data.append([f'{p}th', f'{stock_pct[i]:.2f}%', f'{bench_pct[i]:.2f}%'])
        
        table = ax7.table(cellText=table_data,
                         colLabels=['Percentile', self.stock_symbol, self.benchmark_symbol],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(len(percentiles) + 1):
            if i == 0:
                table[(i, 0)].set_facecolor('#4CAF50')
                table[(i, 1)].set_facecolor('#4CAF50')
                table[(i, 2)].set_facecolor('#4CAF50')
            elif i <= 3:
                table[(i, 0)].set_facecolor('#ffcccc')
                table[(i, 1)].set_facecolor('#ffcccc')
                table[(i, 2)].set_facecolor('#ffcccc')
            elif i == 5:
                table[(i, 0)].set_facecolor('#fff9c4')
                table[(i, 1)].set_facecolor('#fff9c4')
                table[(i, 2)].set_facecolor('#fff9c4')
            elif i >= 7:
                table[(i, 0)].set_facecolor('#c8e6c9')
                table[(i, 1)].set_facecolor('#c8e6c9')
                table[(i, 2)].set_facecolor('#c8e6c9')
        
        ax7.set_title('Percentile Comparison', fontsize=12, fontweight='bold', pad=20)
        
        # 8. Position Sizing
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        fifth_pct_loss = np.percentile(stock_final_returns, 5)
        max_loss = self.starting_capital * (self.max_tolerable_loss_pct / 100)
        
        if fifth_pct_loss < 0:
            recommended = min(max_loss / (abs(fifth_pct_loss) / 100), self.starting_capital)
            recommended_pct = (recommended / self.starting_capital) * 100
            cash_pct = 100 - recommended_pct
            
            sizing_data = [[f'${self.starting_capital:,.0f}'],
                          [f'{self.max_tolerable_loss_pct}%'],
                          [f'{fifth_pct_loss:.2f}%'],
                          [f'${recommended:,.0f}'],
                          [f'{recommended_pct:.1f}%'],
                          [f'{cash_pct:.1f}%']]
            
            sizing_table = ax8.table(cellText=sizing_data,
                                    rowLabels=['Starting Capital',
                                              'Max Loss Tolerance',
                                              '5th Percentile',
                                              'Recommended Position',
                                              'Position %',
                                              'Cash %'],
                                    cellLoc='center',
                                    loc='center',
                                    bbox=[0, 0, 1, 1])
            sizing_table.auto_set_font_size(False)
            sizing_table.set_fontsize(10)
            sizing_table.scale(1, 2.5)
            
            ax8.set_title('Position Sizing Recommendation', fontsize=12, fontweight='bold', pad=20)
        
        # 9. Summary Statistics
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary_data = [
            [f'{self.stock_mu*100:.2f}%', f'{self.benchmark_mu*100:.2f}%'],
            [f'{self.stock_sigma*100:.2f}%', f'{self.benchmark_sigma*100:.2f}%'],
            [f'{self.correlation:.3f}', '1.000'],
            [f'{self.beta:.3f}', '1.000']
        ]
        
        summary_table = ax9.table(cellText=summary_data,
                                 rowLabels=['Ann. Return', 'Ann. Volatility', 'Correlation', 'Beta'],
                                 colLabels=[self.stock_symbol, self.benchmark_symbol],
                                 cellLoc='center',
                                 loc='center',
                                 bbox=[0, 0, 1, 1])
        summary_table.auto_set_font_size(False)
        summary_table.set_fontsize(10)
        summary_table.scale(1, 2.5)
        
        ax9.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)
        
        plt.suptitle(f'Monte Carlo Risk Analysis: {self.stock_symbol} vs {self.benchmark_symbol}\n'
                    f'{self.num_simulations:,} simulations over {self.days_to_simulate} days (DEMO DATA)',
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        
        output_path = f'/mnt/user-data/outputs/monte_carlo_demo_{self.stock_symbol}_vs_{self.benchmark_symbol}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Visualization saved")
        
        plt.close()
        
        return output_path
    
    def run_full_analysis(self):
        """Run complete analysis"""
        self.run_simulation()
        self.calculate_percentiles()
        self.calculate_position_sizing()
        self.analyze_regimes()
        viz_path = self.plot_results()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}")
        
        return viz_path


if __name__ == "__main__":
    
    # DEMO CONFIGURATION
    engine = MonteCarloRiskEngineDemo(
        stock_symbol="TSLA",
        benchmark_symbol="SPY",
        starting_capital=100000,
        days_to_simulate=252,
        num_simulations=25000,
        max_tolerable_loss_pct=20
    )
    
    viz_path = engine.run_full_analysis()
