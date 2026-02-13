# Configuration Guide: Short-Term vs Long-Term Settings

## Understanding the Problem

Your screener found **0 signals** because it was configured for **40-day mean reversion cycles**, but the market (as shown in your SPY chart) is experiencing **10-15 day swing cycles**.

**Think of it like fishing:**
- Long-term config = Deep sea fishing (big fish, rare bites)
- Short-term config = Lake fishing (smaller fish, frequent bites)

---

## Quick Reference Table

| Setting | Long-Term (Original) | Short-Term (Recommended) | Why Change? |
|---------|---------------------|-------------------------|-------------|
| `ROLLING_WINDOW` | 40 days | 10 days | Match the 2-week swings in SPY |
| `Z_SCORE_OVERSOLD` | -2.0 | -1.2 | Lower threshold catches moderate moves |
| `Z_SCORE_OVERBOUGHT` | 2.0 | 1.2 | Lower threshold catches moderate moves |
| `PE_PERCENTILE_THRESHOLD` | 50 | 70 | Less restrictive (was filtering 97 stocks) |
| `USE_FORWARD_PE` | True | False | Disable this filter (too restrictive) |
| Expected Signals | 5-15 | 15-40 | More opportunities in choppy market |
| Hold Time | 4-8 weeks | 1-3 weeks | Faster mean reversion |

---

## The 5 Key Changes Explained

### 1. ROLLING_WINDOW: 40 → 10

**What it does:**
- Calculates the "normal" price range over this many days
- Measures if current price is unusual vs this window

**Why change it:**
```
Long-term (40 days):
├─ Looks at 2-month average
├─ Only triggers on HUGE moves
└─ Misses 1-2 week swings

Short-term (10 days):
├─ Looks at 2-week average
├─ Catches weekly swings
└─ Matches SPY's current chop pattern
```

**Example:**
- Stock normally trades $100
- Drops to $95 in 1 week
- **40-day window:** "Meh, still near 2-month average" ❌
- **10-day window:** "Whoa, 5% drop in a week!" ✅

---

### 2. Z_SCORE_OVERSOLD: -2.0 → -1.2

**What it does:**
- Measures how many standard deviations below average
- -2.0 = Very extreme (happens rarely)
- -1.2 = Moderate (happens more often)

**Why change it:**

```
Think of Z-scores as "weirdness levels":

Z = -1.0: A bit unusual (happens ~16% of time)
Z = -1.5: Pretty unusual (happens ~7% of time)
Z = -2.0: Very unusual (happens ~2.3% of time)  ← Original
Z = -2.5: Extremely rare (happens ~0.6% of time)

Short-term windows have smaller swings, so:
- Z = -1.2 in 10 days is as significant as
- Z = -2.0 in 40 days
```

**Visual:**
```
LONG-TERM (40 days):
Price: ████████████████████ (normal range)
       ↓
       ███ (-2.0 = way outside, rare)

SHORT-TERM (10 days):
Price: ████████ (tighter normal range)
       ↓
       ██ (-1.2 = outside recent range, more common)
```

---

### 3. Z_SCORE_OVERBOUGHT: 2.0 → 1.2

**What it does:**
- Same as oversold, but for upside
- Detects when stock rallied too much too fast

**Why change it:**
- Same logic as oversold
- In choppy markets, ±1.2 sigma moves happen weekly
- In trending markets, need ±2.0 to find real extremes

---

### 4. PE_PERCENTILE_THRESHOLD: 50 → 70

**What it does:**
- Filters stocks by P/E ratio vs their sector
- 50 = only bottom 50% (cheaper half)
- 70 = bottom 70% (allows slightly expensive)

**Why change it:**

**Your results showed:**
```
97 stocks filtered by P/E (46% of universe)
```

This was too restrictive for finding statistical dislocations.

**Philosophy:**
```
LONG-TERM:
├─ Combine value + mean reversion
├─ Want cheap stocks that dropped more
└─ P/E = 50th percentile (strict value filter)

SHORT-TERM:
├─ Focus on statistical dislocation only
├─ Don't care as much about valuation
└─ P/E = 70th percentile (loose filter, avoid junk)
```

**Example:**
- MSFT P/E = 35, Sector median = 27
- Percentile rank = 65th (more expensive than 65% of sector)
- **Long-term (50):** Filtered out ❌
- **Short-term (70):** Passes ✅

---

### 5. USE_FORWARD_PE: True → False

**What it does:**
- Forward P/E = next year's estimated P/E
- When True, also filters by forward P/E percentile

**Why disable it:**

**Your results:**
```
"Forward P/E too high vs sector" - removed many stocks
```

**Problems with forward P/E:**
1. Based on analyst estimates (can be wrong)
2. Not available for all stocks
3. Adds another restrictive filter
4. For short-term mean reversion, forward earnings don't matter much

**Trade-off:**
```
ENABLE Forward P/E:
✅ Better fundamental quality
❌ Fewer signals (97 filtered)
❌ More data dependency

DISABLE Forward P/E:
✅ More signals
✅ Focus on statistical edge
⚠️ May include some overvalued stocks
```

For short-term mean reversion, **statistical dislocation matters more than forward earnings**.

---

## When to Use Each Configuration

### Use LONG-TERM Settings When:

✅ **Market is trending cleanly**
- SPY in strong uptrend or downtrend
- Clear direction, not choppy

✅ **You want fewer, higher-quality signals**
- Only trade 5-10 positions max
- Prefer to hold 4-8 weeks
- Don't want active management

✅ **Looking for structural value + dislocation**
- Want fundamentally cheap stocks
- Willing to wait for mean reversion
- Lower turnover strategy

**Example market conditions:**
```
SPY: Steady climb above 200MA
     Few pullbacks, long trends
     Low VIX (< 15)
     
→ Use 40-day window, ±2.0 Z-score
```

---

### Use SHORT-TERM Settings When:

✅ **Market is choppy/range-bound** ← YOUR CURRENT SITUATION
- SPY bouncing in 678-695 range
- Sharp 10-15 point swings
- No clear trend

✅ **You want more frequent signals**
- Active trading style
- Can manage 15-40 positions
- Check positions daily

✅ **Mean reversion happens quickly**
- Swings resolve in 5-15 days
- Market doesn't sustain trends
- High correlation (sector moves together)

**Example market conditions (YOUR CHART):**
```
SPY: Range 678-695 YTD
     Sharp swings every 1-2 weeks
     Choppy, no sustained trend
     
→ Use 10-day window, ±1.2 Z-score
```

---

## How to Make the Changes

### Option 1: Edit Existing config.py (EASIEST)

Open `config.py` and find/replace these 5 lines:

```python
# Around line 35
ROLLING_WINDOW = 40        # CHANGE TO: 10

# Around line 42-43
Z_SCORE_OVERSOLD = -2.0    # CHANGE TO: -1.2
Z_SCORE_OVERBOUGHT = 2.0   # CHANGE TO: 1.2

# Around line 26
PE_PERCENTILE_THRESHOLD = 50  # CHANGE TO: 70

# Around line 30
USE_FORWARD_PE = True      # CHANGE TO: False
```

Save and run:
```bash
python screener_main.py
```

---

### Option 2: Keep Both Configs (RECOMMENDED)

Create two separate config files:

**config_long_term.py** (your original settings)
```python
ROLLING_WINDOW = 40
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0
PE_PERCENTILE_THRESHOLD = 50
USE_FORWARD_PE = True
```

**config_short_term.py** (new settings)
```python
ROLLING_WINDOW = 10
Z_SCORE_OVERSOLD = -1.2
Z_SCORE_OVERBOUGHT = 1.2
PE_PERCENTILE_THRESHOLD = 70
USE_FORWARD_PE = False
```

**Switch between them:**
```bash
# Use short-term
cp config_short_term.py config.py
python screener_main.py

# Use long-term
cp config_long_term.py config.py
python screener_main.py
```

---

## Expected Results Comparison

### Long-Term Config (Original)
```
Input: 211 stocks
Universe filter: 186 pass
Fundamental filter: 89 pass (97 filtered by P/E)
Statistical filter: 0 pass (no extreme 40-day dislocations)
→ SIGNALS: 0 ❌
```

### Short-Term Config (Modified)
```
Input: 211 stocks
Universe filter: 186 pass (same)
Fundamental filter: ~140 pass (only ~46 filtered)
Statistical filter: ~15-40 pass (catching 10-day swings)
→ SIGNALS: 15-40 ✅
```

**Difference:** You'll get 15-40 signals matching the recent market chop.

---

## Interpreting Signals by Timeframe

### Long-Term Signal Example
```
Ticker: XYZ
Z-Score: -2.3
Window: 40 days
Interpretation: Stock dropped significantly vs 2-month average
                This is rare (only ~1% of time)
                High conviction, structural dislocation
Strategy: Sell put spread 30-45 DTE
Hold time: 4-8 weeks
Position size: 2% of portfolio
```

### Short-Term Signal Example
```
Ticker: XYZ
Z-Score: -1.4
Window: 10 days
Interpretation: Stock sold off vs 2-week average
                This is moderate (happens ~8% of time)
                Quick mean reversion opportunity
Strategy: Sell put spread 7-14 DTE
Hold time: 1-2 weeks
Position size: 1% of portfolio
```

---

## Fine-Tuning Tips

### Too Few Signals Still?

Try even more aggressive:
```python
ROLLING_WINDOW = 5         # 1 week
Z_SCORE_OVERSOLD = -1.0    # Very low threshold
PE_PERCENTILE_THRESHOLD = 80
USE_SECTOR_MEDIAN_PE = False  # Disable P/E entirely
```

### Too Many Signals?

Tighten slightly:
```python
ROLLING_WINDOW = 15        # 3 weeks
Z_SCORE_OVERSOLD = -1.5
PE_PERCENTILE_THRESHOLD = 60
```

### Signals Aren't Working?

Check if you're in a trending market:
```python
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = True  # Only longs in uptrend
```

---

## Real-World Workflow

### Week 1: Test Short-Term Config
```bash
# Monday: Run screener
python screener_main.py

# Results: 25 signals
# Action: Pick top 5 by Z-score magnitude
# Enter: Put spreads on oversold, call spreads on overbought
```

### Week 2: Monitor & Adjust
```bash
# Check positions daily
# Track: Which signals mean-reverted?
# Note: Average hold time
```

### Week 3: Optimize
```
If signals resolved in 3-5 days → Use 5-day window
If signals took 15+ days → Use 20-day window
If signals failed → Check if market started trending
```

---

## Summary

**Your Problem:**
- Market swinging in 10-day cycles
- Config looking for 40-day cycles
- Result: 0 signals

**The Fix:**
```
Change 5 settings:
1. ROLLING_WINDOW: 40 → 10
2. Z_SCORE_OVERSOLD: -2.0 → -1.2
3. Z_SCORE_OVERBOUGHT: 2.0 → 1.2
4. PE_PERCENTILE_THRESHOLD: 50 → 70
5. USE_FORWARD_PE: True → False
```

**Expected Result:**
- 15-40 signals
- Matches SPY's current chop
- 1-3 week holding periods

**Next Step:**
Edit your `config.py` with the 5 changes above and run the screener!
