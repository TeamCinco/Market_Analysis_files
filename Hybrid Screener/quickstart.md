# Quick Start Guide

## 1. Setup (First Time Only)

```bash
# Install dependencies
pip install yfinance pandas numpy xlsxwriter openpyxl

# Verify installation
python -c "import yfinance; print('✓ Ready')"
```

## 2. Configure Your Screener

Edit `config.py` - start with these settings:

```python
# Basic settings for first run
MIN_AVG_VOLUME = 1_000_000
MIN_MARKET_CAP = 2_000_000_000
ROLLING_WINDOW = 40
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0

# Recommended for beginners
USE_REGIME_FILTERS = True
MARKET_TREND_LONG_ONLY = True  # Only long signals in bull market
```

## 3. Prepare Ticker File

Create a file with tickers (one per line or tab-separated):

```
AAPL	5000000
MSFT	4000000
GOOGL	3000000
TSLA	10000000
```

Or just:
```
AAPL
MSFT
GOOGL
TSLA
```

Update path in `config.py`:
```python
TICKER_FILE = "/path/to/your/ticker.txt"
OUTPUT_FILE = "/path/to/output/results.xlsx"
```

## 4. Run Screener

```bash
python screener_main.py
```

You'll see:
1. Sector percentile calculation
2. Regime filter initialization (VIX, SPY trend)
3. Stock-by-stock screening progress
4. Final summary with signals

**Press Ctrl+C anytime to save partial results.**

## 5. Interpret Results

Open the Excel file:

### Green rows (LONG signals)
- Stock is oversold (Z-score ≤ -2)
- Opportunity for upside mean reversion
- **Strategy**: Bull put spread or put credit spread

### Red rows (SHORT signals)
- Stock is overbought (Z-score ≥ +2)
- Opportunity for downside mean reversion
- **Strategy**: Bear call spread or call credit spread

### Check These Columns
- **cluster_risk**: TRUE = multiple signals in same sector (proceed with caution)
- **elevated_vol_regime**: TRUE = higher volatility than usual (adjust position size)
- **vol_percentile**: Current volatility rank vs historical (higher = more risk/premium)

## 6. Example Trade Flow

**Signal Found:**
```
Ticker: XYZ
Signal: LONG
Z-Score: -2.3
Current Price: $50
Realized Vol: 35%
Cluster Risk: FALSE
Elevated Vol: FALSE
```

**Interpretation:**
- XYZ is oversold (Z = -2.3)
- Currently at $50, likely to revert higher
- No sector clustering issues
- Normal volatility regime

**Option Strategy:**
- Sell $48 put (below current price)
- Buy $45 put (protection)
- Collect premium on mean reversion up
- Max risk: $3 per share minus premium collected

## Common First-Run Issues

### "No signals found"
**Cause**: Thresholds too strict
**Fix**: 
```python
# In config.py
Z_SCORE_OVERSOLD = -1.5  # Lower threshold
Z_SCORE_OVERBOUGHT = 1.5
```

### "Too many signals"
**Cause**: Thresholds too loose
**Fix**:
```python
Z_SCORE_OVERSOLD = -2.5  # Raise threshold
Z_SCORE_OVERBOUGHT = 2.5
```

### "Market trend filter blocks all longs"
**Cause**: SPY is below 200MA (bearish regime)
**Fix**: Either wait for market to turn, or disable filter:
```python
USE_MARKET_TREND_FILTER = False
```

### "All stocks filtered by fundamentals"
**Cause**: P/E filters too strict
**Fix**:
```python
PE_PERCENTILE_THRESHOLD = 70  # Allow more expensive stocks
```

## Tuning for Your Style

### Conservative (High Quality, Fewer Signals)
```python
Z_SCORE_OVERSOLD = -2.5
Z_SCORE_OVERBOUGHT = 2.5
PE_PERCENTILE_THRESHOLD = 40
SECTOR_CONCENTRATION_THRESHOLD = 2
USE_REGIME_FILTERS = True
MARKET_TREND_LONG_ONLY = True
```

### Moderate (Balanced)
```python
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0
PE_PERCENTILE_THRESHOLD = 50
SECTOR_CONCENTRATION_THRESHOLD = 3
USE_REGIME_FILTERS = True
```

### Aggressive (More Signals, Active Trading)
```python
Z_SCORE_OVERSOLD = -1.5
Z_SCORE_OVERBOUGHT = 1.5
PE_PERCENTILE_THRESHOLD = 60
SECTOR_CONCENTRATION_THRESHOLD = 5
USE_REGIME_FILTERS = False
```

## Next Steps

1. **Start small**: Paper trade or use small position sizes
2. **Track results**: Keep a spreadsheet of signals vs outcomes
3. **Refine parameters**: Adjust based on your results
4. **Understand Greeks**: Learn delta, theta, vega for spreads
5. **Risk management**: Never risk more than 1-2% per trade

## Getting Help

**Check these first:**
- README.md - Full documentation
- config.py - All parameter explanations
- Excel output - Review cluster risk and vol flags

**Common questions:**
- "Why no signals?" → Adjust Z-score thresholds
- "How to use sector-relative?" → Set `USE_SECTOR_RELATIVE = True`
- "What's a good rolling window?" → 40 days is balanced, 20 is aggressive, 60 is conservative
- "Should I enable VIX filter?" → Yes if you only want to trade in calm markets

## Safety Checklist

Before trading any signal:

- [ ] Check cluster risk flag
- [ ] Check volatility regime flag  
- [ ] Verify P/E makes sense (not broken company)
- [ ] Check current regime state (bull/bear)
- [ ] Confirm liquidity (volume > 1M shares)
- [ ] Size position appropriately
- [ ] Define max loss before entry
- [ ] Have exit plan (time or price based)

---

**Remember**: Screener finds opportunities, you manage risk.