"""
Hybrid Value + Statistical Dislocation Screener
Main orchestration script

Architecture:
1. Universe Filter (volume, market cap, ETF exclusion)
2. Fundamental Survivability Filter (P/E, sector relative valuation)
3. Statistical Dislocation Trigger (Z-score based mean reversion)
4. Regime Filter (VIX, market trend conditioning)
5. Risk-Aware Output (cluster detection, volatility flags)
"""
import sys
import signal
from pathlib import Path

# Import modules
import config
from universe_filter import passes_universe_filter, get_universe_data
from fundamental_filter import (
    get_fundamental_metrics, 
    calculate_sector_percentiles, 
    passes_fundamental_filter
)
from statistical_dislocation import check_dislocation_trigger
from regime_filter import RegimeFilter
from risk_flags import add_risk_flags, generate_risk_summary, print_risk_summary
from excel_output import write_results_to_excel, print_top_signals
from ticker_loader import load_tickers

# Global results for signal handler
RESULTS = []
SECTOR_PERCENTILES = {}

# ============================================================================
# SIGNAL HANDLER FOR CTRL+C
# ============================================================================

def signal_handler(sig, frame):
    """Save results when user hits Ctrl+C"""
    print("\n\n" + "="*80)
    print("INTERRUPTED - Saving partial results...")
    print("="*80)
    
    if RESULTS:
        try:
            # Add risk flags
            flagged_results = add_risk_flags(RESULTS, config)
            
            # Write to Excel
            write_results_to_excel(flagged_results, config.OUTPUT_FILE)
            print(f"\nSaved {len(RESULTS)} signals before exit")
            
            # Print risk summary
            risk_summary = generate_risk_summary(flagged_results, config)
            print_risk_summary(risk_summary)
            
        except Exception as e:
            print(f"Error saving: {e}")
    else:
        print("No signals to save")
    
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# MAIN SCREENING LOGIC
# ============================================================================

def screen_single_stock(ticker, sector_percentiles, regime_filter):
    """
    Screen a single stock through all filters
    
    Returns:
        dict with results or None if filtered out
    """
    # Step 1: Universe Filter
    universe_result = passes_universe_filter(
        ticker, 
        config.MIN_AVG_VOLUME, 
        config.MIN_MARKET_CAP, 
        config.INCLUDE_ETFS
    )
    
    if not universe_result['passed']:
        return {'ticker': ticker, 'status': 'filtered_universe', 'reason': universe_result['reason']}
    
    # Get universe data
    universe_data = get_universe_data(ticker)
    sector = universe_data['sector']
    
    # Step 2: Fundamental Filter
    fundamental_result = passes_fundamental_filter(ticker, sector_percentiles, config)
    
    if not fundamental_result['passed']:
        return {'ticker': ticker, 'status': 'filtered_fundamental', 'reason': fundamental_result['reason']}
    
    # Step 3: Statistical Dislocation
    dislocation_result = check_dislocation_trigger(ticker, config, sector)
    
    if not dislocation_result or not dislocation_result['success']:
        return {'ticker': ticker, 'status': 'no_dislocation', 'reason': 'No statistical signal'}
    
    if not dislocation_result['signal']:
        return {'ticker': ticker, 'status': 'no_signal', 'reason': 'Z-score within thresholds'}
    
    # Step 4: Regime Filter
    regime_result = regime_filter.passes_regime_filter(dislocation_result['signal'])
    
    if not regime_result['passed']:
        return {'ticker': ticker, 'status': 'filtered_regime', 'reason': regime_result['reason']}
    
    # Combine all data into result
    result = {
        'ticker': ticker,
        'status': 'SIGNAL',
        'signal': dislocation_result['signal'],
        'sector': sector,
        'volume': universe_data['volume'],
        'market_cap': universe_data['market_cap'],
        'pe': fundamental_result['metrics']['pe'],
        'sector_median_pe': fundamental_result.get('sector_median_pe'),
        'forward_pe': fundamental_result['metrics']['forward_pe'],
        'z_score': dislocation_result['z_score'],
        'distance_from_mean': dislocation_result['distance_from_mean'],
        'current_price': dislocation_result['current_price'],
        'realized_vol_20d': dislocation_result['realized_vol_20d'],
        'vol_percentile': dislocation_result['vol_percentile'],
        'sector_relative': dislocation_result['sector_relative']
    }
    
    return result


def main():
    global RESULTS, SECTOR_PERCENTILES
    
    print("\n" + "="*80)
    print("HYBRID VALUE + STATISTICAL DISLOCATION SCREENER")
    print("="*80)
    print("\nFramework:")
    print("  1. Universe Filter (volume, market cap)")
    print("  2. Fundamental Survivability (P/E sector-relative)")
    print("  3. Statistical Dislocation (Z-score mean reversion)")
    print("  4. Regime Conditioning (market trend, VIX)")
    print("  5. Risk-Aware Flagging (clusters, volatility)")
    print("\nTIP: Press Ctrl+C to save partial results and exit")
    
    # Load tickers
    print(f"\nLoading tickers from: {config.TICKER_FILE}")
    tickers = load_tickers(config.TICKER_FILE)
    print(f"Found {len(tickers)} tickers")
    
    # Calculate sector percentiles
    print("\n" + "="*80)
    print("CALCULATING SECTOR PERCENTILES")
    print("="*80)
    SECTOR_PERCENTILES = calculate_sector_percentiles(tickers, config)
    
    # Initialize regime filter
    print("\n" + "="*80)
    print("INITIALIZING REGIME FILTERS")
    print("="*80)
    regime_filter = RegimeFilter(config)
    regime_summary = regime_filter.get_regime_summary()
    
    if regime_summary:
        print("\nCurrent Regime State:")
        for key, value in regime_summary.items():
            print(f"  {key}: {value}")
    
    # Run screening
    print("\n" + "="*80)
    print("SCREENING STOCKS")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Z-Score Method: {config.Z_SCORE_METHOD}")
    print(f"  Rolling Window: {config.ROLLING_WINDOW} days")
    print(f"  Oversold Threshold: {config.Z_SCORE_OVERSOLD}")
    print(f"  Overbought Threshold: {config.Z_SCORE_OVERBOUGHT}")
    print(f"  Sector Relative: {config.USE_SECTOR_RELATIVE}")
    
    print("\n" + "-"*80)
    
    filtered_counts = {
        'filtered_universe': 0,
        'filtered_fundamental': 0,
        'no_dislocation': 0,
        'no_signal': 0,
        'filtered_regime': 0,
        'SIGNAL': 0
    }
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        
        result = screen_single_stock(ticker, SECTOR_PERCENTILES, regime_filter)
        
        status = result['status']
        filtered_counts[status] += 1
        
        if status == 'SIGNAL':
            RESULTS.append(result)
            print(f"✓ {result['signal']} (Z: {result['z_score']:.2f}, Vol: {result['realized_vol_20d']:.1f}%)")
        else:
            print(f"✗ {result.get('reason', 'Filtered')}")
        
        # Periodic save
        if i % config.SAVE_INTERVAL == 0 and RESULTS:
            print(f"\n[Auto-saving progress: {len(RESULTS)} signals]")
            try:
                flagged_results = add_risk_flags(RESULTS, config)
                write_results_to_excel(flagged_results, config.OUTPUT_FILE, regime_summary)
            except Exception as e:
                print(f"Warning: Auto-save failed: {e}")
    
    # Final output
    print("\n" + "="*80)
    print("SCREENING COMPLETE")
    print("="*80)
    
    print(f"\nFilter Funnel:")
    print(f"  Total Tickers: {len(tickers)}")
    print(f"  Universe Filtered: {filtered_counts['filtered_universe']}")
    print(f"  Fundamental Filtered: {filtered_counts['filtered_fundamental']}")
    print(f"  No Statistical Dislocation: {filtered_counts['no_dislocation']}")
    print(f"  Z-Score Within Thresholds: {filtered_counts['no_signal']}")
    print(f"  Regime Filtered: {filtered_counts['filtered_regime']}")
    print(f"  ▶ SIGNALS GENERATED: {filtered_counts['SIGNAL']}")
    
    if RESULTS:
        # Add risk flags
        flagged_results = add_risk_flags(RESULTS, config)
        
        # Generate and print risk summary
        risk_summary = generate_risk_summary(flagged_results, config)
        print_risk_summary(risk_summary)
        
        # Print top signals
        print_top_signals(flagged_results, n=config.MAX_DISPLAY_ROWS)
        
        # Write final Excel
        write_results_to_excel(flagged_results, config.OUTPUT_FILE, regime_summary)
        
        print("\n" + "="*80)
        print("USAGE NOTES")
        print("="*80)
        print("\n✓ These are DISLOCATION signals, not buy/sell recommendations")
        print("✓ Use signals to construct defined-risk option spreads")
        print("✓ LONG signals = oversold, mean reversion expected upward")
        print("✓ SHORT signals = overbought, mean reversion expected downward")
        print("✓ Check cluster_risk flag for sector concentration")
        print("✓ Check elevated_vol_regime flag for volatility spikes")
        
    else:
        print("\nNo signals found matching criteria")
        print("Consider adjusting Z-score thresholds or filters in config.py")
    
    print("\n" + "="*80)
    print("DONE")
    print("="*80)

if __name__ == "__main__":
    main()