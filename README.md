# Monte Carlo Risk Engine

A Monte Carlo risk analysis tool for single equity price distributions. Maps forward downside risk and tail structure to support position sizing and strike placement for options execution.

This tool provides statistical context, not predictions.

---

## What It Does

Runs 25,000 Monte Carlo simulations over a configurable horizon to answer:

> "Under realistic dispersion assumptions, how wide can outcomes be and where is the real left tail?"

Designed to support risk management and options structure decisions (primarily credit verticals) on liquid equities.

---

## Core Concept

The engine separates two questions:

1. **Backward-looking:**
   Where does a realized price move fall in the simulated distribution?

2. **Forward-looking:**
   From this price, what does downside risk look like over the next N days?

This distinction matters:

* **Backward percentiles** = statistical context for a move that already happened
* **Forward percentiles** = strike placement and spread width discipline

---

## Simulation Model

The engine does not use vanilla Geometric Brownian Motion. The core simulation has three departures from standard Gaussian assumptions:

**Student-t shocks (df=5):** Random shocks are drawn from a fat-tailed distribution instead of normal. This produces more realistic extreme move frequency. Scaled to unit variance so the average day is unchanged but tail events occur more often.

**EWMA volatility clustering (lambda=0.94):** Volatility evolves through each simulation path. A large move on day 10 increases volatility on day 11. Calm periods stay calm. This introduces path dependence that constant-sigma GBM ignores.

**Distributed jump process (2% daily probability, -4% magnitude):** Discrete downside shocks can occur on any day across the full simulation, not just at expiration. Models gap risk from earnings, macro events, or sudden sentiment shifts.

**Drift:** Uses a risk-free rate proxy (currently 4.2%) instead of historical mean return. Historical equity drift is unstable on short horizons and adds noise without improving tail estimation.

**Volatility stress ladder:** Each run produces three scenario sets at 1.0x, 1.25x, and 1.5x base volatility to show how the distribution widens under stress.

---

## Risk State Score

A composite measure of current tail conditions. Four components normalized to 0-1 and averaged into a single score (0-100):

| Component | What It Measures | Normalization Range |
|-----------|-----------------|-------------------|
| Vol Regime Ratio | 20-day realized vol / 100-day realized vol | 0.7 - 1.5 |
| Tail Thickness | CVaR(99) / VaR(99) | 1.1 - 1.6 |
| Jump Frequency | % of historical days with >3% drops | 0 - 3% |
| Distribution Width | 95th percentile minus 5th percentile | 10% - 60% |

**Interpretation:**
* Below 35 = Compressed regime. Tails are tight.
* 35-65 = Neutral. Normal dispersion.
* Above 65 = Elevated. Distribution is wide, tails are thick. Respect the risk.

The score does not predict direction. It tells you how fragile the distribution is so you can calibrate aggression on spread placement and position sizing.

---

## Project Structure

```
/Tail End Risk/
├── run_analysis.py                  (runner / parameter config)
└── /Mc Engine/
    ├── monte_carlo_risk_engine.py   (orchestrator class)
    ├── mc_data.py                   (data download via yfinance)
    ├── mc_stats.py                  (volatility + drift calculation)
    ├── mc_simulation.py             (Student-t, EWMA, jumps, stress ladder)
    ├── mc_percentiles.py            (percentile + CVaR calculation)
    ├── mc_risk_state.py             (4-component risk state score)
    └── mc_viz.py                    (8-panel dashboard visualization)
```

**Total:** ~950 lines

---

## Usage

Configure parameters in `run_analysis.py`:

```python
STOCK_SYMBOL = "MSFT"
DAYS_TO_SIMULATE = 45       # match your trade horizon (45 DTE = 45)
NUM_SIMULATIONS = 25000
HISTORICAL_WINDOW = 252     # lookback for vol calc (252 = 1yr, 126 = 6mo)
```

Run:

```bash
python run_analysis.py
```

---

## Output

### Dashboard (`/output/monte_carlo_risk_engine/`)

An 8-panel visualization:

| Panel | What It Shows |
|-------|--------------|
| Price Path Percentiles | Simulated price fan (5th through 95th) |
| Return Distribution | Final return histogram with 1st, 5th, median lines |
| Return Percentiles | Table of returns at each percentile |
| Risk Summary | VaR, CVaR at 95% and 99% confidence |
| Stress Distributions | Overlaid histograms for 1.0x / 1.25x / 1.5x vol |
| Tail Shift Under Stress | How 5th and 1st percentile move under stress |
| Strike Probability Guide | Percentile to strike price mapping with breach probability |
| Risk State Engine | All 4 components + composite score + regime classification |

### Terminal Output

```
Annual Volatility:    26.40%
VaR (95%):           -28.49%
CVaR (95%):          -36.16%
Risk State Score:     71.3/100
Regime:               Elevated
```

---

## Backtest Mode (Realized Move Analysis)

Used to determine where an actual price move falls in the distribution.

```python
CUSTOM_STOCK_PRICE = 400.0      # price before move
TARGET_PRICE_TO_CHECK = 380.0   # price after move
```

Outputs percentile rank of the move and statistical context.

This answers: "How unusual was this drop relative to current volatility regime?"

Note: this is not historical replay. It applies current vol conditions to a hypothetical starting price. Valid for regime-aware context, not for true backtesting.

---

## Tunable Parameters

| Parameter | Default | What It Controls |
|-----------|---------|-----------------|
| `DAYS_TO_SIMULATE` | 90 | Simulation horizon. Set to match your DTE. |
| `HISTORICAL_WINDOW` | 252 | Lookback for base volatility. Shorter = more responsive. |
| `risk_free_rate` | 0.042 | Drift proxy. Set in `monte_carlo_risk_engine.py`. |
| `jump_prob` | 0.02 | Daily jump probability. Set in `mc_simulation.py`. |
| `jump_magnitude` | -0.04 | Jump size. Negative = downside shock. |
| `df` | 5 | Student-t degrees of freedom. Lower = fatter tails. |
| `lambda_` | 0.94 | EWMA decay. Higher = slower vol response. |
| `vol_multipliers` | [1.0, 1.25, 1.5] | Stress scenarios. |

---

## Standard Workflow

1. Run analysis on watchlist
2. Note percentile price levels and risk state score
3. Set alerts near relevant percentile boundaries
4. When triggered, run backtest with actual price for statistical context
5. Use forward percentiles to map return levels to strike prices
6. Check risk state score to calibrate spread width and sizing aggression
7. Verify fundamentals, volatility regime, and IV independently
8. Execute if conditions pass

---

## What This Tool Tells You

* Where price sits in a simulated return distribution
* Expected volatility over the holding period
* Tail risk severity under base and stressed vol
* How fragile current conditions are (risk state score)
* Percentile-to-strike price mappings for spread placement

### What It Does Not Do

* Predict direction
* Generate buy/sell signals
* Replace fundamental or macro analysis
* Price options or estimate implied volatility

It provides statistical context only.

---

## Missing Piece: IV vs Realized Volatility

The engine uses realized volatility. Execution requires comparing that to implied volatility independently.

| Realized Vol | Current IV | Interpretation | Action |
|-------------|-----------|----------------|--------|
| 17% | 14% | IV cheap | Don't sell premium |
| 17% | 18% | Fair | Marginal |
| 17% | 25%+ | IV expensive | Favorable for selling |

This comparison determines whether the statistical edge is tradable. The engine does not perform it.

---

## Technical Details

* Modified GBM framework with three non-Gaussian departures
* Student-t distributed shocks (df=5, scaled to unit variance)
* EWMA conditional volatility (lambda=0.94, RiskMetrics standard)
* Poisson-style jump overlay (distributed through full path)
* Risk-free rate drift proxy
* Random seed = 42 (reproducibility)
* CVaR = mean of worst tail outcomes (expected shortfall)

---

## Limitations

* Parametric model, not empirical bootstrap
* Does not model earnings events or known catalysts
* Single asset only, no correlation or portfolio context
* Backtest mode uses current vol regime, not historical conditions
* Jump parameters are assumptions, not calibrated to each name
* No implied volatility integration

---

## Intended Use Case

Risk management and strike placement discipline for options trading on liquid equities. The Monte Carlo maps the tail structure. You still must validate the regime, check fundamentals, confirm IV conditions, and define failure criteria independently.