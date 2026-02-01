# Monte Carlo Risk Analysis Engine

A professional-grade Monte Carlo simulation tool for analyzing investment risk, position sizing, and stock-benchmark relationships.

---

## 🎯 What This Does

This tool helps you answer the critical questions:

1. **"How wrong can I be and still survive?"** (Position sizing under fat tails)
2. **"What's the relationship between my stock and the market?"** (Correlation & Beta analysis)
3. **"How does performance change in different market regimes?"** (Regime analysis)

**This is NOT a strategy backtester.** It's a **risk analysis framework** that shows you the distribution of possible outcomes so YOU can make informed decisions.

---

## 📊 What You Get

### Statistical Analysis:
- Percentile outcomes (1st, 5th, 10th, 25th, 50th, 75th, 90th, 95th, 99th)
- Correlation between stock and benchmark
- Beta (volatility ratio)
- Annualized returns and volatility

### Position Sizing:
- Recommended position size based on 5th percentile survivability
- Maximum tolerable loss calculations
- Capital allocation recommendations

### Regime Analysis:
- Performance under LOW, MEDIUM, and HIGH volatility regimes
- Shows when your stock becomes too risky

### Visualizations:
- Price path distributions (fan charts)
- Return distributions (histograms)
- Stock vs benchmark scatter plot (shows correlation visually)
- Percentile comparison tables
- Position sizing recommendations

---

## 🚀 Quick Start

### Option 1: Demo Version (No Internet Required)

```bash
python demo_monte_carlo.py
```

Uses realistic synthetic data to demonstrate functionality.

**To modify parameters**, edit these lines in `demo_monte_carlo.py`:

```python
engine = MonteCarloRiskEngineDemo(
    stock_symbol="TSLA",              # Change this
    benchmark_symbol="SPY",           # Change this
    starting_capital=100000,          # Your capital
    days_to_simulate=252,             # 252 = 1 year
    num_simulations=25000,            # More = slower but more accurate
    max_tolerable_loss_pct=20         # Max % loss you can handle
)
```

### Option 2: Real Data Version (Requires yfinance access)

```bash
python run_analysis.py
```

**To modify parameters**, edit these lines in `run_analysis.py`:

```python
STOCK_SYMBOL = "TSLA"           # Any stock ticker
BENCHMARK_SYMBOL = "SPY"        # Any benchmark ticker
STARTING_CAPITAL = 100000       # Your capital
MAX_TOLERABLE_LOSS_PCT = 20     # Max % loss
DAYS_TO_SIMULATE = 252          # Trading days
NUM_SIMULATIONS = 25000         # Monte Carlo paths
```

---

## 📖 Understanding the Output

### Example Output:

```
PERCENTILE ANALYSIS (252 days)
Percentile           TSLA          SPY
----------------------------------------
1th %ile            -62.45%      -24.28%
5th %ile            -49.69%      -15.94%  ← THIS IS THE KEY NUMBER
10th %ile            -40.88%      -10.89%
50th %ile              5.35%        9.41%  ← Median outcome
95th %ile            120.39%       42.14%
```

### What This Means:

**5th Percentile = -49.69%**
- There's a 5% chance (1 in 20) you lose 49.69% or more
- This is your "bad outcome" you need to survive
- 95% of the time, you'll do BETTER than this

**50th Percentile = +5.35%**
- This is the median outcome
- Half the time you do better, half the time worse
- NOT what you should size your position for

**95th Percentile = +120.39%**
- There's a 5% chance you gain 120% or more
- This is your "good outcome" (upside tail)

---

## 💰 Position Sizing Logic

### The Problem:
Most traders size for the median outcome and get destroyed by tail risk.

### The Solution:
Size so that even the 5th percentile doesn't blow you up.

### Example:

```
Starting Capital: $100,000
Max Tolerable Loss: 20% ($20,000)
5th Percentile Loss: -49.69%

If you invest full $100k:
- 5th percentile loss = $49,690 ❌ (exceeds your tolerance)

Recommended Position: $40,250
- 5th percentile loss = $20,000 ✓ (within tolerance)
- Keep $59,750 in cash
```

**Key insight:** You don't invest $100k just because you have it. You invest based on how much you can LOSE in the tail scenario.

---

## 🔬 Regime Analysis

Markets aren't static. Volatility changes. Your edge might disappear in different regimes.

### Example Output:

```
Regime          5th %ile     50th %ile    95th %ile   
-------------------------------------------------------
LOW VOL             -33.82%      10.87%      87.18%
MEDIUM VOL          -49.45%       5.51%     121.93%
HIGH VOL            -70.24%      -8.14%     172.96%  ← Median is negative!
```

### What This Tells You:

**In LOW VOL:**
- 5th percentile = -33.82% (manageable)
- Median = +10.87% (positive expectation)
- **Action:** Full position size OK

**In MEDIUM VOL:**
- 5th percentile = -49.45% (getting risky)
- Median = +5.51% (still positive)
- **Action:** Reduce position size

**IN HIGH VOL:**
- 5th percentile = -70.24% (catastrophic)
- Median = -8.14% (negative expectation!)
- **Action:** STOP TRADING or go to cash

**The edge:** Most traders keep trading the same way in all regimes. This shows you WHEN to reduce exposure or stop.

---

## 🎓 Key Concepts Explained

### What is Beta?

**Beta = How much the stock moves relative to the benchmark**

```
Beta = 1.0 → Stock moves exactly with the market
Beta = 1.5 → Stock moves 50% MORE than the market
Beta = 0.5 → Stock moves 50% LESS than the market
```

**Example:** If SPY drops 10% and your stock has Beta = 1.8:
- Expected stock drop = 10% × 1.8 = -18%

### What is Correlation?

**Correlation = How closely stock and benchmark move together**

```
Correlation = +1.0 → Perfect positive relationship (always move together)
Correlation = +0.7 → Strong positive relationship
Correlation = 0.0 → No relationship
Correlation = -1.0 → Perfect negative relationship (move opposite)
```

**Why it matters:** 
- High correlation (0.7+) → Stock follows the market
- Low correlation (0.3-) → Stock has independent drivers
- If correlation breaks down, your assumptions are invalid

### What is a Percentile?

**Simple example:**

Imagine 100 possible futures:
- Worst outcome (1st percentile): You're better than 1% of outcomes
- 5th percentile: You're better than 5% of outcomes
- 50th percentile (median): Right in the middle
- 95th percentile: You're better than 95% of outcomes

**For trading:**
- Don't size for the median (50th percentile)
- Size for the BAD outcome (5th percentile)
- Because you only need ONE bad outcome to blow up

---

## 🛠️ Customization Guide

### Change the stock/benchmark:

```python
stock_symbol="AAPL"         # Apple
benchmark_symbol="QQQ"      # NASDAQ instead of S&P 500
```

### Change time horizon:

```python
days_to_simulate=126        # 6 months (126 trading days)
days_to_simulate=252        # 1 year (252 trading days)
days_to_simulate=504        # 2 years (504 trading days)
```

### Change risk tolerance:

```python
max_tolerable_loss_pct=10   # Conservative (10% max loss)
max_tolerable_loss_pct=20   # Moderate (20% max loss)
max_tolerable_loss_pct=30   # Aggressive (30% max loss)
```

### Increase simulation accuracy:

```python
num_simulations=50000       # More paths = slower but more accurate
```

---

## 📁 Files Included

1. **monte_carlo_risk_engine.py**
   - Full implementation with yfinance (requires internet)
   - Fetches real market data
   - Use this for production analysis

2. **demo_monte_carlo.py**
   - Demo version with synthetic data
   - Works without internet
   - Great for testing and learning

3. **run_analysis.py**
   - Simple interface for the real data version
   - Easy parameter modification
   - Just edit variables at the top

4. **README.md**
   - This file
   - Complete documentation

---

## 🧠 Why This Approach Works

### Traditional approach (WRONG):
```
"My strategy wins 60% of the time!"
[Doesn't check tail risk]
[Sizes for median outcome]
[Gets destroyed when 5th percentile hits]
```

### Monte Carlo approach (CORRECT):
```
"The 5th percentile shows -50% loss. Can I survive that?"
[Sizes position so 5th percentile = tolerable loss]
[Checks when assumptions break (regime shifts)]
[Survives indefinitely]
```

### The difference:
- Traditional traders blow up eventually
- Monte Carlo traders survive the tails

---

## 💡 How to Use This in Practice

### Step 1: Run the analysis
```bash
python demo_monte_carlo.py  # Or run_analysis.py for real data
```

### Step 2: Check the 5th percentile
```
"5th Percentile: -49.69%"
```

### Step 3: Ask yourself
```
"Can I handle a -50% loss on this position?"
```

### Step 4: Size accordingly
```
If NO:  Follow the recommended position size
If YES: You can allocate more capital
```

### Step 5: Monitor regime
```
Check current market volatility
If volatility spikes → reduce position
If volatility compresses → can increase position
```

---

## ⚠️ Important Notes

### This is NOT:
- ❌ A strategy backtester
- ❌ A prediction tool
- ❌ A guarantee of future performance

### This IS:
- ✅ A risk analysis framework
- ✅ A position sizing tool
- ✅ A regime detection system
- ✅ A distribution analysis tool

### Remember:
- **Monte Carlo shows what CAN happen, not what WILL happen**
- **The strategy doesn't matter if you can't survive the tails**
- **Size for the 5th percentile, not the median**
- **Regimes change — your edge might disappear**

---

## 🔄 Next Steps

1. Run the demo to understand the output
2. Modify parameters to test different scenarios
3. Try different stocks/benchmarks
4. Use the position sizing recommendations
5. Monitor regime changes in live trading

---

## 📚 Further Reading

Key concepts to research:
- Fat-tailed distributions
- Value at Risk (VaR)
- Geometric Brownian Motion
- Position sizing (Kelly Criterion)
- Regime detection

---

## 🙋 FAQ

**Q: Why use 5th percentile instead of worst case?**
A: Worst case (1st percentile) is often too extreme and unrealistic. 5th percentile (1 in 20) is statistically significant and practical.

**Q: Can I use this for options/futures/crypto?**
A: Yes, but adjust volatility parameters accordingly. Crypto has much higher vol.

**Q: Should I size for 5th or 10th percentile?**
A: Depends on risk tolerance. 5th is more conservative, 10th is more aggressive.

**Q: What if my 5th percentile is positive?**
A: Lucky you! Low downside risk. But still check correlation and regime sensitivity.

**Q: How often should I re-run this?**
A: Weekly or when market volatility changes significantly.

---

**Built with:**
- Python 3
- NumPy (Monte Carlo simulation)
- Pandas (data handling)
- Matplotlib/Seaborn (visualization)
- yfinance (market data)

---

## 📧 Output Location

All visualizations are saved to:
```
/mnt/user-data/outputs/monte_carlo_*.png
```

You can download these files and review them at any time.

---

**Remember:** The edge isn't in predicting the future. It's in surviving all possible futures.

Good luck, and size responsibly. 🎯
