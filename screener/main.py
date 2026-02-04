"""
Monte Carlo Stock Screener
Analyzes all stocks in ticker.txt and outputs to Excel
"""
import sys
import signal
from pathlib import Path

# Add engine directory to path
engine_path = Path(__file__).parent / "engine"
sys.path.insert(0, str(engine_path))

from engine.ticker_loader import load_tickers
from engine.screener_engine import analyze_stock
from engine.excel_writer import write_results_to_excel

# ============================================================================
# CONFIGURATION
# ============================================================================

TICKER_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker_filtered.txt"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_results.xlsx"

DAYS_TO_SIMULATE = 90
NUM_SIMULATIONS = 10000
HISTORICAL_WINDOW = 252*6

# Global results list for signal handler
RESULTS = []

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
            write_results_to_excel(RESULTS, OUTPUT_FILE)
            print(f"\nSaved {len(RESULTS)} results before exit")
        except Exception as e:
            print(f"Error saving: {e}")
    else:
        print("No results to save")
    
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# MAIN
# ============================================================================

def main():
    global RESULTS
    
    print("\n" + "="*80)
    print("MONTE CARLO STOCK SCREENER")
    print("="*80)
    print("\nTIP: Press Ctrl+C to save partial results and exit")
    
    # Load tickers
    print(f"\nLoading tickers from: {TICKER_FILE}")
    tickers = load_tickers(TICKER_FILE)
    print(f"Found {len(tickers)} tickers")
    
    # Run analysis
    print(f"\nRunning Monte Carlo analysis ({NUM_SIMULATIONS:,} simulations, {DAYS_TO_SIMULATE} days)")
    print("="*80)
    
    save_interval = 100  # Save every 100 stocks
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        
        result = analyze_stock(
            ticker,
            days_to_simulate=DAYS_TO_SIMULATE,
            num_simulations=NUM_SIMULATIONS,
            historical_window=HISTORICAL_WINDOW
        )
        
        if result['success']:
            RESULTS.append(result)
            print(f"✓ (drop: {result['drop_from_high_pct']:.1f}%, p10: {result['p10']:.1f}%)")
        else:
            print(f"✗ Failed")
        
        # Periodic save every 100 stocks
        if i % save_interval == 0 and RESULTS:
            print(f"\n[Auto-saving progress: {len(RESULTS)} stocks completed]")
            try:
                write_results_to_excel(RESULTS, OUTPUT_FILE)
            except Exception as e:
                print(f"Warning: Auto-save failed: {e}")
    
    # Final save and analysis
    print("\n" + "="*80)
    print(f"Successful: {len(RESULTS)}/{len(tickers)}")
    
    if RESULTS:
        import pandas as pd
        df = pd.DataFrame(RESULTS)
        
        # Show selling opportunities
        print("\n" + "="*80)
        print("SELLING OPPORTUNITIES:")
        print("="*80)
        
        selling_zone = df[
            (df['drop_from_high_pct'] <= -10) &  # Already dropped 10%+
            (df['p10'] >= -10) &                  # Limited forward downside
            (df['p10'] <= -5) &
            (df['volatility'] >= 15) &            # Enough vol for premium
            (df['volatility'] <= 30)              # Not too crazy
        ]
        
        print(f"\nFound {len(selling_zone)} candidates:")
        print(f"  Criteria: Dropped 10%+, forward p10 -5% to -10%, vol 15-30%\n")
        
        if len(selling_zone) > 0:
            display = selling_zone[['ticker', 'current_price', 'drop_from_high_pct', 'p10', 'volatility']].head(20)
            print(display.to_string(index=False))
        else:
            print("  None found matching all criteria")
        
        # Write final Excel
        write_results_to_excel(RESULTS, OUTPUT_FILE)
    
    print("\n" + "="*80)
    print("DONE - Open Excel and filter for your criteria")
    print("="*80)

if __name__ == "__main__":
    main()