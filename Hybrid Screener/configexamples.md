# Configuration Examples

This file contains pre-configured setups for different trading styles and market conditions.

## Example 1: Conservative Long-Only (Bull Market)

**Use case**: Only take high-conviction long signals in confirmed bull market

```python
# Universe
MIN_AVG_VOLUME = 2_000_000          # Higher volume for better liquidity
MIN_MARKET_CAP = 5_000_000_000      # Large cap only
INCLUDE_ETFS = False

# Fundamentals - Very selective
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 40         # Bottom 40% only (undervalued)
EXCLUDE_NEGATIVE_PE = True
USE_FORWARD_PE = True
FORWARD_PE_PERCENTILE_THRESHOLD = 40

# Statistical - High threshold
ROLLING_WINDOW = 60                  # Longer window, less noise
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -2.5              # Only extreme oversold
Z_SCORE_OVERBOUGHT = 2.5             # Disabled in practice (long-only)

# Regime - Strict
USE_REGIME_FILTERS = True
USE_VIX_FILTER = True
MAX_VIX_THRESHOLD = 20               # Only low vol environments
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = True        # Only longs when SPY > 200MA
MARKET_TREND_SHORT_ONLY = False

# Risk - Low tolerance
SECTOR_CONCENTRATION_THRESHOLD = 2   # Max 2 signals per sector
HIGH_VOL_PERCENTILE = 70
```

**Expected outcome**: 5-15 high-quality long signals in bull market

---

## Example 2: Balanced Mean Reversion

**Use case**: Equal opportunity long/short, moderate conviction

```python
# Universe
MIN_AVG_VOLUME = 1_000_000
MIN_MARKET_CAP = 2_000_000_000
INCLUDE_ETFS = False

# Fundamentals - Moderate
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 50         # Sector median
EXCLUDE_NEGATIVE_PE = True
USE_FORWARD_PE = True
FORWARD_PE_PERCENTILE_THRESHOLD = 50

# Statistical - Balanced
ROLLING_WINDOW = 40
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0

# Regime - Moderate
USE_REGIME_FILTERS = True
USE_VIX_FILTER = False               # Allow higher vol
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = True        # Longs when SPY > 200MA
MARKET_TREND_SHORT_ONLY = False      # Shorts anytime

# Risk - Moderate
SECTOR_CONCENTRATION_THRESHOLD = 3
HIGH_VOL_PERCENTILE = 75
```

**Expected outcome**: 15-30 signals mix of long/short

---

## Example 3: Aggressive Short-Term Scalping

**Use case**: Active trading, more signals, shorter holding periods

```python
# Universe
MIN_AVG_VOLUME = 3_000_000           # Very liquid only
MIN_MARKET_CAP = 1_000_000_000       # Allow smaller caps
INCLUDE_ETFS = False

# Fundamentals - Relaxed
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 60         # Top 60%
EXCLUDE_NEGATIVE_PE = False          # Allow negative PE
USE_FORWARD_PE = False               # Don't care about forward

# Statistical - Sensitive
ROLLING_WINDOW = 20                  # Short-term
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -1.5              # Lower threshold
Z_SCORE_OVERBOUGHT = 1.5

# Regime - Minimal
USE_REGIME_FILTERS = False           # Trade in all conditions

# Risk - Aggressive
SECTOR_CONCENTRATION_THRESHOLD = 5
HIGH_VOL_PERCENTILE = 80
```

**Expected outcome**: 30-60+ signals, requires active management

---

## Example 4: Sector-Relative Swing Trading

**Use case**: Trade stock-specific moves vs sector, ignore macro

```python
# Universe
MIN_AVG_VOLUME = 1_500_000
MIN_MARKET_CAP = 3_000_000_000
INCLUDE_ETFS = False

# Fundamentals
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 50
EXCLUDE_NEGATIVE_PE = True

# Statistical - Sector-Relative Mode
ROLLING_WINDOW = 40
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0
USE_SECTOR_RELATIVE = True           # KEY: Measure vs sector ETF

SECTOR_ETFS = {
    'Technology': 'XLK',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Utilities': 'XLU',
    'Communication Services': 'XLC'
}

# Regime - Disable (sector-relative handles it)
USE_REGIME_FILTERS = False

# Risk
SECTOR_CONCENTRATION_THRESHOLD = 3
HIGH_VOL_PERCENTILE = 75
```

**Expected outcome**: Stock-specific dislocations regardless of sector trend

---

## Example 5: Bear Market Short-Only

**Use case**: Only short overbought stocks in bear market

```python
# Universe
MIN_AVG_VOLUME = 2_000_000
MIN_MARKET_CAP = 3_000_000_000
INCLUDE_ETFS = False

# Fundamentals - Expensive stocks (better short candidates)
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 70         # Top 70% (more expensive)
EXCLUDE_NEGATIVE_PE = True

# Statistical - High threshold for shorts
ROLLING_WINDOW = 50
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -3.0              # Disabled in practice
Z_SCORE_OVERBOUGHT = 2.0             # Short overbought

# Regime - Bearish only
USE_REGIME_FILTERS = True
USE_VIX_FILTER = False
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = False
MARKET_TREND_SHORT_ONLY = True       # Only shorts when SPY < 200MA

# Risk
SECTOR_CONCENTRATION_THRESHOLD = 2   # Careful in bear markets
HIGH_VOL_PERCENTILE = 70
```

**Expected outcome**: 5-20 short signals in bear market

---

## Example 6: High-Quality Value + Momentum Fade

**Use case**: Fade overbought moves in quality value stocks

```python
# Universe
MIN_AVG_VOLUME = 1_000_000
MIN_MARKET_CAP = 5_000_000_000       # Large cap only

# Fundamentals - Premium quality
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 35         # Bottom 35% (deep value)
EXCLUDE_NEGATIVE_PE = True
USE_FORWARD_PE = True
FORWARD_PE_PERCENTILE_THRESHOLD = 35
USE_EV_EBITDA = True
EV_EBITDA_THRESHOLD = 12
USE_FCF_YIELD = True
MIN_FCF_YIELD = 0.04                 # 4% minimum

# Statistical - Both directions
ROLLING_WINDOW = 50
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -2.0              # Oversold quality = buy
Z_SCORE_OVERBOUGHT = 2.0             # Overbought quality = fade

# Regime - Moderate
USE_REGIME_FILTERS = True
USE_VIX_FILTER = True
MAX_VIX_THRESHOLD = 25
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = True

# Risk - Conservative
SECTOR_CONCENTRATION_THRESHOLD = 2
HIGH_VOL_PERCENTILE = 70
```

**Expected outcome**: 5-10 premium quality signals

---

## Example 7: Earnings Season Volatility Harvesting

**Use case**: Trade elevated IV during earnings season

```python
# Universe - Very liquid
MIN_AVG_VOLUME = 5_000_000
MIN_MARKET_CAP = 10_000_000_000      # Mega cap only

# Fundamentals - Don't care much
USE_SECTOR_MEDIAN_PE = True
PE_PERCENTILE_THRESHOLD = 60
EXCLUDE_NEGATIVE_PE = False

# Statistical - Standard
ROLLING_WINDOW = 30                  # Medium-term
Z_SCORE_METHOD = "returns"
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0

# Regime - Minimal
USE_REGIME_FILTERS = False

# Risk - Focus on volatility
SECTOR_CONCENTRATION_THRESHOLD = 4
HIGH_VOL_PERCENTILE = 85             # Higher threshold (we want high vol)
```

**Note**: Manually filter output for stocks with earnings in next 1-2 weeks

---

## Seasonal Configurations

### Q4 Tax Loss Harvesting Season (Nov-Dec)
```python
# Look for oversold quality stocks being dumped for tax reasons
ROLLING_WINDOW = 30
Z_SCORE_OVERSOLD = -2.5
PE_PERCENTILE_THRESHOLD = 30         # Quality only
USE_MARKET_TREND_FILTER = False      # Don't care about regime
```

### January Effect (Early Jan)
```python
# Fade year-end rallies, buy Jan dips
ROLLING_WINDOW = 20
Z_SCORE_OVERSOLD = -2.0              # Buy dips
Z_SCORE_OVERBOUGHT = 2.5             # Fade rallies
```

### Summer Doldrums (Jun-Aug)
```python
# Lower volume, wider spreads needed
MIN_AVG_VOLUME = 2_000_000
ROLLING_WINDOW = 60                  # Longer window
Z_SCORE_OVERSOLD = -2.5
USE_VIX_FILTER = True
MAX_VIX_THRESHOLD = 15               # Very calm markets
```

---

## Testing New Configurations

When experimenting with new settings:

1. **Start conservative** → Loosen gradually
2. **Run on 100-200 tickers first** → See signal count
3. **Check risk flags** → Ensure not too concentrated
4. **Paper trade 2-4 weeks** → Validate edge
5. **Size small initially** → 0.5% risk per trade max
6. **Track statistics** → Win rate, avg hold time, drawdowns

## Configuration Checklist

Before running a new config:

- [ ] Z-score thresholds are reasonable (-3 to +3 range)
- [ ] Rolling window makes sense (20-60 days typical)
- [ ] Fundamental filters aren't too strict (>5% of universe passes)
- [ ] Regime filters align with market conditions
- [ ] Risk thresholds set appropriately
- [ ] Ticker file path is correct
- [ ] Output file path is valid
- [ ] Save interval set (50-100 typical)

---

**Pro Tip**: Keep multiple config files (config_conservative.py, config_aggressive.py) and swap them based on market regime.