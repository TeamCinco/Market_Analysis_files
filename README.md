# Monte Carlo Risk Engine

Quick Monte Carlo simulation for position sizing and risk analysis. Runs thousands of price paths based on historical volatility and correlation to benchmark.

## Structure

```
/Tail End Risk/
├── run_analysis.py              # Main script - configure and run here
└── /Mc Engine/
    ├── monte_carlo_risk_engine.py   # Main orchestrator
    ├── mc_data.py                   # Data download via yfinance
    ├── mc_stats.py                  # Volatility, correlation, beta
    ├── mc_simulation.py             # Monte Carlo simulation
    ├── mc_percentiles.py            # Percentile calculations
    └── mc_viz.py                    # Plotting functions
```

## Usage

Edit `run_analysis.py` parameters:

```python
STOCK_SYMBOL = "CAT"
BENCHMARK_SYMBOL = "SPY"
STARTING_CAPITAL = 1000
MAX_TOLERABLE_LOSS_PCT = 14
DAYS_TO_SIMULATE = 30
NUM_SIMULATIONS = 25000
HISTORICAL_WINDOW = 252*6
```

Run:
```bash
cd "/path/to/Tail End Risk"
python run_analysis.py
```

## What it does

1. Downloads historical data (yfinance)
2. Calculates annualized volatility, correlation, beta
3. Runs correlated Monte Carlo simulations (geometric Brownian motion)
4. Calculates percentiles (1st, 5th, 10th, 25th, 50th, 75th, 90th, 95th, 99th) *as of 2/1/26 I added VAR and Cvar calculations in the output.*
5. Recommends position size based on 5th percentile loss vs max tolerable loss
6. Generates 9-panel visualization

## Output

Saves to: `/Users/jazzhashzzz/Documents/Market_Analysis_files/output/monte_carlo_risk_engine/`

Contains:
- Price path distributions (normalized)
- Return distributions
- Stock vs benchmark scatter (beta regression)
- Rolling 30-day correlation
- Percentile comparison table
- Position sizing recommendation
- Statistical summary

## Backtest Mode

Set custom starting prices to backtest from specific price levels:

```python
CUSTOM_STOCK_PRICE = 400.0      # Start from this price instead of current
CUSTOM_BENCHMARK_PRICE = 580.0  # Optional benchmark price
```

Output filename will include "BACKTEST" tag.

## Target Price Analysis

Check where a specific price falls in the distribution:

```python
TARGET_PRICE_TO_CHECK = 380.0
```

Terminal output shows:
- Percentile rank of target price
- Distance from key percentiles (1st, 5th, 10th, 25th, 50th)
- Mean reversion potential to median
- Interpretation (extreme tail, oversold, etc.)

Use case: Stock drops from $400 to $380, run with `CUSTOM_STOCK_PRICE = 400.0` and `TARGET_PRICE_TO_CHECK = 380.0` to see if the drop was a 5th percentile event (potential entry) or 50th percentile (normal variance).

## Modifying Code

**Add new statistic:**
Edit `mc_stats.py`, add calculation, return in dict

**Add new chart:**
Edit `mc_viz.py`, add `_plot_your_chart()` function, call in `create_visualization()`

**Change simulation method:**
Edit `mc_simulation.py`, modify `run_monte_carlo()` logic

**Add new risk metric:**
Edit `mc_percentiles.py`, add calculation function

## Dependencies

```
yfinance
numpy
pandas
matplotlib
```

## Notes

- Random seed = 42 for reproducibility
- 252 trading days = 1 year
- Correlation uses Cholesky decomposition for correlated random variables
- Position sizing: `recommended_position = min(max_loss_dollars / abs(5th_percentile_loss), starting_capital)`
- Uses geometric Brownian motion: `S_t = S_0 * exp((μ - σ²/2)t + σW_t)`

## Limitations

- Assumes log-normal returns (fat tails underestimated)
- Uses historical volatility (may not reflect regime changes)
- Correlation assumes stable relationship
- No transaction costs, slippage, or liquidity constraints
- Single-asset analysis (no portfolio effects)


#How to use:
You don't run the script every day. Run it once per week (Sunday night) for each stock on your watchlist. Note the percentile prices from the output image and set alerts at the 10th percentile level. Then go live your life.

When an alert triggers (stock dropped 5-10% in a day), open run_analysis.py and set:
pythonCUSTOM_STOCK_PRICE = 400.0       *Price before the drop*
TARGET_PRICE_TO_CHECK = 380.0    *Current price after drop*

Run it. Terminal shows the percentile rank. If it's 5th-15th percentile, continue. If >15th, ignore it - not extreme enough.
Next, check fundamentals in 5 minutes: Why did it drop? Call an employee or check industry data. Business still strong?
Then check IV: Pull current implied vol from your broker, compare to the realized vol number in your Monte Carlo output. IV lower than realized = options are cheap.

If all three align (percentile extreme + fundamentals intact + IV cheap), buy one 90-120 day OTM call with $800-1000. Target exit at median recovery (50th percentile price from your table). Stop if fundamentals change or stock hits 1st percentile.
That's it. 3-5 trades per year max.