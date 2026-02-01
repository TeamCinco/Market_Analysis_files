"""
Interactive Monte Carlo Risk Analysis
Easy parameter configuration - just modify the variables below
"""

from monte_carlo_risk_engine import MonteCarloRiskEngine

# ============================================================================
# USER INPUTS - MODIFY THESE PARAMETERS
# ============================================================================

# Stock and Benchmark
STOCK_SYMBOL = "CAT"           # Change to any stock (e.g., "AAPL", "NVDA", "MSFT")
BENCHMARK_SYMBOL = "SPY"        # Change to any benchmark (e.g., "QQQ", "DIA", "IWM")

# Capital and Risk Parameters
STARTING_CAPITAL = 1000       # Your starting capital in dollars
MAX_TOLERABLE_LOSS_PCT = 14     # Max % loss you can handle (e.g., 15, 20, 25)

# Simulation Parameters
DAYS_TO_SIMULATE = 30        # Trading days to simulate (252 = 1 year, 126 = 6 months)
NUM_SIMULATIONS = 25000         # Number of Monte Carlo paths (more = slower but more accurate)
HISTORICAL_WINDOW = 252*6         # Days to look back for volatility calculation

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("MONTE CARLO RISK ANALYSIS ENGINE")
print("="*80)
print(f"\nConfiguration:")
print(f"  Stock:              {STOCK_SYMBOL}")
print(f"  Benchmark:          {BENCHMARK_SYMBOL}")
print(f"  Starting Capital:   ${STARTING_CAPITAL:,.2f}")
print(f"  Max Loss Tolerance: {MAX_TOLERABLE_LOSS_PCT}%")
print(f"  Simulation Days:    {DAYS_TO_SIMULATE}")
print(f"  Monte Carlo Paths:  {NUM_SIMULATIONS:,}")
print("="*80)

# Initialize the engine
engine = MonteCarloRiskEngine(
    stock_symbol=STOCK_SYMBOL,
    benchmark_symbol=BENCHMARK_SYMBOL,
    starting_capital=STARTING_CAPITAL,
    days_to_simulate=DAYS_TO_SIMULATE,
    num_simulations=NUM_SIMULATIONS,
    historical_window=HISTORICAL_WINDOW,
    max_tolerable_loss_pct=MAX_TOLERABLE_LOSS_PCT
)

# Run the full analysis
try:
    viz_path = engine.run_full_analysis()
    
    print(f"\n{'='*80}")
    print("SUCCESS! Analysis complete.")
    print(f"{'='*80}")
    print(f"\nVisualization saved to: {viz_path}")
    print("\nYou can now:")
    print("  1. View the output image")
    print("  2. Modify parameters above and re-run")
    print("  3. Try different stocks/benchmarks")
    
except Exception as e:
    print(f"\n{'='*80}")
    print("ERROR occurred:")
    print(f"{'='*80}")
    print(f"{str(e)}")
    print("\nPlease check:")
    print("  - Stock/benchmark symbols are valid")
    print("  - You have internet connection for data download")
    print("  - yfinance can access the symbols")