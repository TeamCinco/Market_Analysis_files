"""Visualization functions"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

def create_visualization(data):
    """Create complete visualization - data dict has all needed values"""
    print("\nGenerating visualization...")
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle(
        f'Monte Carlo Risk Analysis: {data["stock_symbol"]} vs {data["benchmark_symbol"]}\n'
        f'{data["num_simulations"]:,} simulations over {data["days_to_simulate"]} days',
        fontsize=16, fontweight='bold'
    )
    
    # Price paths
    ax1 = fig.add_subplot(gs[0, 0])
    _plot_price_paths(ax1, data["stock_paths"], data["stock_symbol"], data["stock_price"], data["days_to_simulate"])
    
    ax2 = fig.add_subplot(gs[0, 1])
    _plot_price_paths(ax2, data["benchmark_paths"], data["benchmark_symbol"], data["benchmark_price"], data["days_to_simulate"])
    
    # Return distributions
    ax3 = fig.add_subplot(gs[0, 2])
    _plot_return_distribution(ax3, data["stock_final_returns"], data["stock_symbol"])
    
    ax4 = fig.add_subplot(gs[1, 0])
    _plot_return_distribution(ax4, data["benchmark_final_returns"], data["benchmark_symbol"])
    
    # Scatter and correlation
    ax5 = fig.add_subplot(gs[1, 1])
    _plot_scatter(ax5, data)
    
    ax6 = fig.add_subplot(gs[1, 2])
    _plot_rolling_correlation(ax6, data)
    
    # Tables
    ax7 = fig.add_subplot(gs[2, 0])
    _plot_percentile_table(ax7, data)
    
    ax8 = fig.add_subplot(gs[2, 1])
    _plot_position_sizing(ax8, data)
    
    ax9 = fig.add_subplot(gs[2, 2])
    _plot_statistical_summary(ax9, data)
    
    # Save
    output_dir = Path('/Users/jazzhashzzz/Documents/Market_Analysis_files/output/monte_carlo_risk_engine')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if data.get("custom_stock_price") is not None:
        filename = f'monte_carlo_{data["stock_symbol"]}_BACKTEST_{timestamp}.png'
    else:
        filename = f'monte_carlo_{data["stock_symbol"]}_{timestamp}.png'
    
    output_path = output_dir / filename
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(output_path)

def _plot_price_paths(ax, paths, symbol, starting_price, days_to_simulate):
    normalized_paths = (paths / starting_price) * 100
    percentiles_to_plot = [5, 25, 50, 75, 95]
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
    
    for i, p in enumerate(percentiles_to_plot):
        percentile_path = np.percentile(normalized_paths, p, axis=1)
        ax.plot(percentile_path, label=f'{p}th percentile', color=colors[i], linewidth=2)
    
    ax.fill_between(range(days_to_simulate), np.percentile(normalized_paths, 5, axis=1),
                     np.percentile(normalized_paths, 95, axis=1), alpha=0.2, color='blue',
                     label='5th-95th percentile range')
    
    ax.set_xlabel('Trading Days', fontsize=10)
    ax.set_ylabel('Normalized Price (Start = 100)', fontsize=10)
    ax.set_title(f'{symbol} - Price Path Distribution', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

def _plot_return_distribution(ax, returns, symbol):
    ax.hist(returns, bins=100, alpha=0.7, color='blue', edgecolor='black')
    p5 = np.percentile(returns, 5)
    p50 = np.percentile(returns, 50)
    p95 = np.percentile(returns, 95)
    ax.axvline(p5, color='red', linestyle='--', linewidth=2, label='5th percentile')
    ax.axvline(p50, color='yellow', linestyle='--', linewidth=2, label='Median')
    ax.axvline(p95, color='green', linestyle='--', linewidth=2, label='95th percentile')
    ax.set_xlabel('Return (%)', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title(f'{symbol} - Final Return Distribution', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

def _plot_scatter(ax, data):
    ax.scatter(data["benchmark_final_returns"], data["stock_final_returns"], alpha=0.3, s=1, color='blue')
    z = np.polyfit(data["benchmark_final_returns"], data["stock_final_returns"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(data["benchmark_final_returns"].min(), data["benchmark_final_returns"].max(), 100)
    ax.plot(x_line, p(x_line), "r-", linewidth=2, label=f'Beta = {data["beta"]:.2f}')
    ax.set_xlabel(f'{data["benchmark_symbol"]} Return (%)', fontsize=10)
    ax.set_ylabel(f'{data["stock_symbol"]} Return (%)', fontsize=10)
    ax.set_title(f'{data["stock_symbol"]} vs {data["benchmark_symbol"]} Returns', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

def _plot_rolling_correlation(ax, data):
    stock_prices = data["stock_data"]['Close'].iloc[-data["historical_window"]:]
    benchmark_prices = data["benchmark_data"]['Close'].iloc[-data["historical_window"]:]
    stock_returns = stock_prices.pct_change()
    benchmark_returns = benchmark_prices.pct_change()
    rolling_corr = stock_returns.rolling(30).corr(benchmark_returns)
    ax.plot(rolling_corr.index, rolling_corr.values, color='purple', linewidth=2)
    ax.axhline(y=data["correlation"], color='red', linestyle='--', linewidth=2, label=f'Average = {data["correlation"]:.3f}')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Correlation', fontsize=10)
    ax.set_title('30-Day Rolling Correlation', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

def _plot_percentile_table(ax, data):
    ax.axis('tight')
    ax.axis('off')
    table_data = []
    percentiles_to_show = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    for p in percentiles_to_show:
        stock_val = data["stock_percentiles"][data["stock_percentiles"]['percentile'] == p]['return'].values[0]
        bench_val = data["benchmark_percentiles"][data["benchmark_percentiles"]['percentile'] == p]['return'].values[0]
        table_data.append([f'{p}th', f'{stock_val:.2f}%', f'{bench_val:.2f}%'])
    
    table = ax.table(cellText=table_data, colLabels=['Percentile', data["stock_symbol"], data["benchmark_symbol"]],
                     cellLoc='center', loc='center', colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    for i, row in enumerate(table_data):
        if i < 3:
            table[(i+1, 1)].set_facecolor('#ffcccc')
            table[(i+1, 2)].set_facecolor('#ffcccc')
        elif i == 4:
            table[(i+1, 1)].set_facecolor('#ffffcc')
            table[(i+1, 2)].set_facecolor('#ffffcc')
        elif i >= 6:
            table[(i+1, 1)].set_facecolor('#ccffcc')
            table[(i+1, 2)].set_facecolor('#ccffcc')
    
    for j in range(3):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Percentile Comparison', fontsize=12, fontweight='bold', pad=20)

def _plot_position_sizing(ax, data):
    ax.axis('tight')
    ax.axis('off')
    loss_5th = data["stock_percentiles"][data["stock_percentiles"]['percentile'] == 5]['return'].values[0]
    capital_at_risk = abs(loss_5th) / 100 * data["starting_capital"]
    max_loss_dollars = data["max_tolerable_loss_pct"] / 100 * data["starting_capital"]
    
    if abs(loss_5th) > 0:
        recommended_position = min(max_loss_dollars / abs(loss_5th) * 100, data["starting_capital"])
    else:
        recommended_position = data["starting_capital"]
    
    position_pct = (recommended_position / data["starting_capital"]) * 100
    cash_pct = 100 - position_pct
    
    table_data = [
        ['Starting Capital', f'${data["starting_capital"]:,.2f}'],
        ['Max Loss Tolerance', f'{data["max_tolerable_loss_pct"]}%'],
        ['', ''],
        ['5th Percentile Loss', f'{loss_5th:.2f}%'],
        ['Recommended Position', f'${recommended_position:,.2f}'],
        ['Position %', f'{position_pct:.1f}%'],
        ['Cash %', f'{cash_pct:.1f}%'],
    ]
    
    table = ax.table(cellText=table_data, cellLoc='left', loc='center', colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('Position Sizing Recommendation', fontsize=12, fontweight='bold', pad=20)

def _plot_statistical_summary(ax, data):
    ax.axis('tight')
    ax.axis('off')
    table_data = [
        ['', data["stock_symbol"], data["benchmark_symbol"]],
        ['Ann. Return', f'{data["stock_expected_return"]*100:.2f}%', f'{data["benchmark_expected_return"]*100:.2f}%'],
        ['Ann. Volatility', f'{data["stock_volatility"]*100:.2f}%', f'{data["benchmark_volatility"]*100:.2f}%'],
        ['Correlation', f'{data["correlation"]:.3f}', '1.000'],
        ['Beta', f'{data["beta"]:.3f}', '1.000'],
    ]
    
    table = ax.table(cellText=table_data, cellLoc='center', loc='center', colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    for j in range(3):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)