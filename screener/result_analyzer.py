"""
Find Selling Opportunities from Screener Results
Simple filter for credit spread setups
"""

import pandas as pd
import os


INPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_results.xlsx"


def find_selling_opportunities(df):
    """
    Find stocks ready for selling credit spreads
    
    Criteria:
    1. Already dropped 10%+ from high (backward extreme)
    2. Forward p10 between -10% and -5% (limited additional downside)
    3. Volatility 15-30% (tradeable range)
    """
    
    # Filter for selling zone
    selling_zone = df[
        (df['drop_from_high_pct'] <= -10) &  # Already extreme
        (df['p10'] >= -10) &                  # Limited forward risk
        (df['p10'] <= -5) &
        (df['volatility'] >= 15) &            # Enough premium
        (df['volatility'] <= 30) &            # Not crazy
        (df['success'] == True)
    ].copy()
    
    # Sort by drop magnitude (most extreme first)
    selling_zone = selling_zone.sort_values('drop_from_high_pct')
    
    return selling_zone


def print_opportunities(df):
    """Print selling opportunities in readable format"""
    
    print("\n" + "="*80)
    print("CREDIT SPREAD OPPORTUNITIES")
    print("="*80)
    print(f"\nFound {len(df)} candidates")
    print("\nCriteria:")
    print("  ✓ Already dropped 10%+ from recent high")
    print("  ✓ Forward p10 between -5% and -10% (limited additional downside)")
    print("  ✓ Volatility 15-30% (manageable)")
    print("\n" + "="*80)
    
    if len(df) == 0:
        print("\nNo opportunities found matching criteria")
        return
    
    print(f"\n{'Ticker':<8} {'Price':<10} {'High':<10} {'Drop%':<10} {'Fwd p10':<10} {'Vol%':<8} {'Action'}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        ticker = row['ticker']
        price = row['current_price']
        high = row['recent_high']
        drop = row['drop_from_high_pct']
        p10 = row['p10']
        vol = row['volatility']
        
        print(f"{ticker:<8} ${price:<9.2f} ${high:<9.2f} {drop:<9.1f}% {p10:<9.1f}% {vol:<7.1f}% INVESTIGATE")
    
    print("\n" + "="*80)
    print("NEXT STEPS for each candidate:")
    print("="*80)
    print("1. Run individual MC with backtest mode (confirm percentile rank)")
    print("2. Check fundamentals (earnings intact? no major issues?)")
    print("3. Check IV Rank manually (need >70 for selling)")
    print("4. Verify VIX <28 (regime check)")
    print("5. If all pass → Sell credit spread at 10th percentile strike")
    print("\n")


def show_top_picks(df, n=5):
    """Show top N picks with reasoning"""
    
    if len(df) == 0:
        return
    
    print("="*80)
    print(f"TOP {min(n, len(df))} PICKS (Most Extreme Drops + Low Forward Risk)")
    print("="*80)
    
    for i, (_, row) in enumerate(df.head(n).iterrows(), 1):
        print(f"\n{i}. {row['ticker']} - ${row['current_price']:.2f}")
        print(f"   Recent High: ${row['recent_high']:.2f}")
        print(f"   Drop: {row['drop_from_high_pct']:.1f}% (backward extreme)")
        print(f"   Forward p10: {row['p10']:.1f}% (limited additional downside)")
        print(f"   Volatility: {row['volatility']:.1f}% (manageable)")
        
        # Calculate potential strikes
        strike_10th = row['current_price'] * (1 + row['p10']/100)
        strike_5th = row['current_price'] * (1 + row['p5']/100)
        
        print(f"   Suggested Spread:")
        print(f"     Short: ${strike_10th:.2f} (10th percentile)")
        print(f"     Long:  ${strike_5th:.2f} (5th percentile)")
        print(f"     Width: ${abs(strike_10th - strike_5th):.2f}")


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Screener results not found at {INPUT_FILE}")
        print("Run the screener first: python main.py")
        return
    
    # Load results
    df = pd.read_excel(INPUT_FILE)
    
    # Find opportunities
    opportunities = find_selling_opportunities(df)
    
    # Print results
    print_opportunities(opportunities)
    show_top_picks(opportunities, n=5)
    
    # Save to separate file
    if len(opportunities) > 0:
        output_file = INPUT_FILE.replace('.xlsx', '_opportunities.xlsx')
        opportunities.to_excel(output_file, index=False)
        print(f"Opportunities saved to: {output_file}\n")


if __name__ == "__main__":
    main()