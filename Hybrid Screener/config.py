"""
Configuration for Value + Statistical Dislocation Screener
SHORT-TERM OPTIMIZED (10-day mean reversion cycles)

CHANGES FROM ORIGINAL:
- ROLLING_WINDOW: 40 → 10 (catch 2-week swings)
- Z_SCORE thresholds: ±2.0 → ±1.2 (lower threshold for shorter window)
- PE_PERCENTILE: 50 → 70 (less restrictive)
- USE_FORWARD_PE: True → False (disabled, was filtering too many)
- REGIME_FILTERS: True → False (choppy market doesn't need regime filter)

All parameters are user-configurable here
"""

# ============================================================================
# UNIVERSE FILTERS
# ============================================================================

# Volume filter (shares/day)
MIN_AVG_VOLUME = 1_000_000  # 1M shares/day

# Market cap filter (USD)
MIN_MARKET_CAP = 2_000_000_000  # $2B (mid-cap threshold)

# Include ETFs in screening
INCLUDE_ETFS = False

# ============================================================================
# FUNDAMENTAL SURVIVABILITY FILTERS
# ============================================================================

# P/E ratio filtering
USE_SECTOR_MEDIAN_PE = True  # If True, compare to sector; if False, use absolute threshold
PE_PERCENTILE_THRESHOLD = 70  # ← CHANGED: 50 → 70 (allow slightly more expensive stocks)
ABSOLUTE_PE_MAX = 50  # ← CHANGED: 25 → 50 (if not using sector-relative)

# Forward P/E (if available)
USE_FORWARD_PE = False  # ← CHANGED: True → False (DISABLED - was filtering 97 stocks)
FORWARD_PE_PERCENTILE_THRESHOLD = 70  # ← CHANGED: 50 → 70 (if re-enabled)

# Additional fundamental filters (optional)
USE_EV_EBITDA = False
EV_EBITDA_THRESHOLD = 15

USE_FCF_YIELD = False
MIN_FCF_YIELD = 0.05  # 5% minimum

# Exclude negative P/E stocks
EXCLUDE_NEGATIVE_PE = False  # ← CHANGED: True → False (allow negative P/E for short-term)

# ============================================================================
# STATISTICAL DISLOCATION PARAMETERS
# ============================================================================

# Rolling window for mean and std deviation (trading days)
ROLLING_WINDOW = 5  # ← CHANGED: 40 → 10 (2 weeks instead of 2 months)

# Z-score calculation method
Z_SCORE_METHOD = "returns"  # Options: "returns" or "prices"

# Z-score thresholds
Z_SCORE_OVERSOLD = -0.8  # ← CHANGED: -2.0 → -1.2 (catch moderate oversold)
Z_SCORE_OVERBOUGHT = 0.8  # ← CHANGED: 2.0 → 1.2 (catch moderate overbought)

# Historical data window for statistics (trading days)
HISTORICAL_WINDOW = 60  # ← CHANGED: 252 → 126 (6 months instead of 1 year)

# ============================================================================
# SECTOR-RELATIVE OPTION
# ============================================================================

# Use sector-relative performance instead of absolute
USE_SECTOR_RELATIVE = False  # Try True if you want stock-specific moves only

# Sector ETF mapping (for sector-relative mode)
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

# ============================================================================
# REGIME FILTERS (RISK CONDITIONING)
# ============================================================================

# Enable regime filtering
USE_REGIME_FILTERS = False  # ← CHANGED: True → False (market is choppy, not trending)

# VIX filter
USE_VIX_FILTER = False
MAX_VIX_THRESHOLD = 30  # ← CHANGED: 25 → 30 (higher threshold if re-enabled)

# Market trend filter (SPY above 200-day MA)
USE_MARKET_TREND_FILTER = False  # ← CHANGED: True → False (disabled for choppy markets)
MARKET_TREND_TICKER = 'SPY'
MARKET_TREND_MA_PERIOD = 200

# Directional filter
MARKET_TREND_LONG_ONLY = False  # ← CHANGED: True → False (allow both directions)
MARKET_TREND_SHORT_ONLY = False  # Only short signals when SPY < 200 MA

# ============================================================================
# RISK-AWARE OUTPUT PARAMETERS
# ============================================================================

# Cluster risk detection
SECTOR_CONCENTRATION_THRESHOLD = 5  # ← CHANGED: 3 → 5 (allow more clustering in choppy markets)

# Volatility regime detection
HIGH_VOL_PERCENTILE = 75  # Flag if current vol > 75th percentile of historical

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# File paths
TICKER_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/company_tickers.json"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/dislocation_screener_results.xlsx"

# Auto-save interval
SAVE_INTERVAL = 50  # Save every 50 stocks

# Display settings
MAX_DISPLAY_ROWS = 30


# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================
"""
SHORT-TERM MEAN REVERSION SETTINGS (Current Config)
---------------------------------------------------
Window: 10 days (2 weeks)
Thresholds: ±1.2 Z-score
Fundamental: Relaxed (70th percentile, no forward P/E)
Regime: Disabled (for choppy markets)
Expected: 15-40 signals
Hold time: 5-15 days
Strategy: 7-14 DTE option spreads

TO SWITCH BACK TO LONG-TERM:
----------------------------
ROLLING_WINDOW = 40
Z_SCORE_OVERSOLD = -2.0
Z_SCORE_OVERBOUGHT = 2.0
PE_PERCENTILE_THRESHOLD = 50
USE_FORWARD_PE = True
EXCLUDE_NEGATIVE_PE = True
USE_REGIME_FILTERS = True
USE_MARKET_TREND_FILTER = True
MARKET_TREND_LONG_ONLY = True

Expected: 5-15 signals
Hold time: 20-40 days
Strategy: 30-45 DTE option spreads

TO GO ULTRA SHORT-TERM (MORE AGGRESSIVE):
-----------------------------------------
ROLLING_WINDOW = 5
Z_SCORE_OVERSOLD = -1.0
Z_SCORE_OVERBOUGHT = 1.0
PE_PERCENTILE_THRESHOLD = 80
USE_SECTOR_MEDIAN_PE = False

Expected: 30-80+ signals
Hold time: 2-7 days
Strategy: 0-7 DTE option spreads
"""