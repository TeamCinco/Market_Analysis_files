"""
Automated Monte Carlo Stock Screener
Tests multiple stocks against multiple benchmarks and ranks by criteria
"""

import numpy as np
import pandas as pd
from monte_carlo_risk_engine import MonteCarloRiskEngine
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Stock universe (diverse sectors)
STOCKS = {
    # Technology
    "AAPL": "Apple",
    "MSFT": "Microsoft", 
    "GOOGL": "Google",
    "NVDA": "NVIDIA",
    "META": "Meta",
    "AMD": "AMD",
    
    # Financials
    "JPM": "JPMorgan",
    "BAC": "Bank of America",
    "V": "Visa",
    "MA": "Mastercard",
    "GS": "Goldman Sachs",
    
    # Healthcare
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PFE": "Pfizer",
    "LLY": "Eli Lilly",
    
    # Consumer
    "AMZN": "Amazon",
    "WMT": "Walmart",
    "HD": "Home Depot",
    "MCD": "McDonalds",
    "COST": "Costco",
    
    # Energy
    "XOM": "Exxon",
    "CVX": "Chevron",
    
    # Industrials
    "BA": "Boeing",
    "CAT": "Caterpillar",
    
    # Volatile/Growth
    "TSLA": "Tesla",
}

# Benchmarks
BENCHMARKS = {
    "SPY": "S&P 500",
    "QQQ": "NASDAQ",
    "IWM": "Russell 2000",
}

# Screening criteria (from our discussion)
CRITERIA = {
    "max_5th_percentile_loss": -20,      # Max 20% loss at 5th percentile
    "max_volatility": 35,                # Max 35% annual volatility
    "min_median_return": 8,              # Min 8% median return
    "min_sharpe_ratio": 0.5,             # Min Sharpe ratio
    "min_correlation": 0.4,              # Min correlation with benchmark
    "max_correlation": 0.85,             # Max correlation
    "max_beta": 1.5,                     # Max beta
    "high_vol_median_positive": True,    # Must stay positive in high vol
}

# Simulation parameters
STARTING_CAPITAL = 100000
MAX_TOLERABLE_LOSS_PCT = 20
DAYS_TO_SIMULATE = 252
NUM_SIMULATIONS = 10000  # Increase to 25000 for production
HISTORICAL_WINDOW = 252

# ============================================================================
# CORE LOGIC
# ============================================================================

def run_quick_analysis(stock, benchmark):
    """Run Monte Carlo without full visualization"""
    try:
        engine = MonteCarloRiskEngine(
            stock_symbol=stock,
            benchmark_symbol=benchmark,
            starting_capital=STARTING_CAPITAL,
            days_to_simulate=DAYS_TO_SIMULATE,
            num_simulations=NUM_SIMULATIONS,
            historical_window=HISTORICAL_WINDOW,
            max_tolerable_loss_pct=MAX_TOLERABLE_LOSS_PCT
        )
        
        engine.fetch_data()
        engine.calculate_statistics()
        engine.run_simulation()
        
        # Calculate metrics
        stock_final = engine.stock_simulations[-1]
        returns = (stock_final / 100 - 1) * 100
        
        fifth_pct = np.percentile(returns, 5)
        median = np.percentile(returns, 50)
        ninetyfifth = np.percentile(returns, 95)
        sharpe = (engine.stock_mu - 0.02) / engine.stock_sigma
        
        # High vol regime test
        vol_high = engine.stock_sigma * 1.5
        temp_sims = np.zeros((DAYS_TO_SIMULATE + 1, 1000))
        temp_sims[0] = 100
        dt = 1/252
        
        for t in range(1, DAYS_TO_SIMULATE + 1):
            shock = np.random.standard_normal(1000)
            temp_sims[t] = temp_sims[t-1] * np.exp(
                (engine.stock_mu - 0.5 * vol_high**2) * dt +
                vol_high * np.sqrt(dt) * shock
            )
        
        high_vol_median = np.median((temp_sims[-1] / 100 - 1) * 100)
        
        # Position sizing
        if fifth_pct < 0:
            max_loss = STARTING_CAPITAL * (MAX_TOLERABLE_LOSS_PCT / 100)
            rec_position = min(max_loss / (abs(fifth_pct) / 100), STARTING_CAPITAL)
            position_pct = (rec_position / STARTING_CAPITAL) * 100
        else:
            position_pct = 100
        
        return {
            'success': True,
            'stock': stock,
            'benchmark': benchmark,
            'fifth_percentile': fifth_pct,
            'median_return': median,
            'ninetyfifth_percentile': ninetyfifth,
            'volatility': engine.stock_sigma * 100,
            'correlation': engine.correlation,
            'beta': engine.beta,
            'sharpe_ratio': sharpe,
            'high_vol_median': high_vol_median,
            'position_pct': position_pct,
        }
        
    except Exception as e:
        return {'success': False, 'stock': stock, 'benchmark': benchmark, 'error': str(e)}


def score_stock(stats):
    """Score stock against criteria"""
    score = 100
    failures = []
    
    if stats['fifth_percentile'] < CRITERIA['max_5th_percentile_loss']:
        score -= 20
        failures.append(f"5th: {stats['fifth_percentile']:.1f}%")
    
    if stats['volatility'] > CRITERIA['max_volatility']:
        score -= 15
        failures.append(f"Vol: {stats['volatility']:.1f}%")
    
    if stats['median_return'] < CRITERIA['min_median_return']:
        score -= 20
        failures.append(f"Median: {stats['median_return']:.1f}%")
    
    if stats['sharpe_ratio'] < CRITERIA['min_sharpe_ratio']:
        score -= 10
        failures.append(f"Sharpe: {stats['sharpe_ratio']:.2f}")
    
    if stats['correlation'] < CRITERIA['min_correlation']:
        score -= 10
        failures.append(f"Corr low: {stats['correlation']:.2f}")
    elif stats['correlation'] > CRITERIA['max_correlation']:
        score -= 5
        failures.append(f"Corr high: {stats['correlation']:.2f}")
    
    if stats['beta'] > CRITERIA['max_beta']:
        score -= 10
        failures.append(f"Beta: {stats['beta']:.2f}")
    
    if CRITERIA['high_vol_median_positive'] and stats['high_vol_median'] < 0:
        score -= 10
        failures.append("High vol negative")
    
    return max(score, 0), failures


def screen_all():
    """Screen all stocks vs all benchmarks"""
    print("\n" + "="*100)
    print("MONTE CARLO STOCK SCREENER")
    print("="*100)
    print(f"Stocks: {len(STOCKS)} | Benchmarks: {len(BENCHMARKS)} | Combinations: {len(STOCKS) * len(BENCHMARKS)}")
    print("="*100)
    
    results = []
    total = len(STOCKS) * len(BENCHMARKS)
    current = 0
    
    for stock, stock_name in STOCKS.items():
        for bench, bench_name in BENCHMARKS.items():
            current += 1
            print(f"[{current}/{total}] {stock} vs {bench}...", end=" ")
            
            stats = run_quick_analysis(stock, bench)
            
            if stats['success']:
                score, failures = score_stock(stats)
                stats['score'] = score
                stats['failures'] = failures
                stats['stock_name'] = stock_name
                stats['bench_name'] = bench_name
                results.append(stats)
                print(f"✓ {score:.0f}/100")
            else:
                print(f"✗ {stats['error'][:30]}")
    
    return results


def display_results(results):
    """Display ranked results"""
    # Filter only successful results that have a score
    successful = [r for r in results if r.get('success') and 'score' in r]
    
    if not successful:
        print("\n" + "="*100)
        print("ERROR: No stocks successfully analyzed")
        print("="*100)
        return pd.DataFrame()
    
    df = pd.DataFrame(successful)
    df = df.sort_values('score', ascending=False)
    
    print("\n" + "="*100)
    print("TOP 10 STOCKS")
    print("="*100)
    
    for idx, row in df.head(10).iterrows():
        print(f"\n{row['stock']} ({row['stock_name']}) vs {row['benchmark']} - {row['score']:.0f}/100")
        print(f"  5th: {row['fifth_percentile']:>7.2f}% | Med: {row['median_return']:>7.2f}% | 95th: {row['ninetyfifth_percentile']:>7.2f}%")
        print(f"  Vol: {row['volatility']:>6.1f}% | Corr: {row['correlation']:>5.2f} | Beta: {row['beta']:>5.2f} | Pos: {row['position_pct']:.0f}%")
        if row['failures']:
            print(f"  ⚠️  {', '.join(row['failures'][:2])}")
    
    print("\n" + "="*100)
    print("BOTTOM 5 STOCKS")
    print("="*100)
    
    for idx, row in df.tail(5).iterrows():
        print(f"{row['stock']} vs {row['benchmark']} - {row['score']:.0f}/100 | {', '.join(row['failures'][:3])}")
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    
    passing = df[df['score'] >= 70]
    print(f"Passing (score ≥70): {len(passing)}/{len(df)}")
    
    if len(passing) > 0:
        print(f"\nAverage metrics (passing stocks):")
        print(f"  5th: {passing['fifth_percentile'].mean():.2f}% | Med: {passing['median_return'].mean():.2f}%")
        print(f"  Vol: {passing['volatility'].mean():.1f}% | Corr: {passing['correlation'].mean():.2f} | Beta: {passing['beta'].mean():.2f}")
    
    # Save
    output = '/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screening_results.csv'
    df.to_csv(output, index=False)
    print(f"\n✓ Results saved: {output}")
    
    return df


def build_portfolio(results, n=5):
    """Build portfolio from top stocks"""
    # Filter successful results with scores
    successful = [r for r in results if r.get('success') and 'score' in r]
    
    if not successful:
        print("\n" + "="*100)
        print("ERROR: No stocks available for portfolio")
        print("="*100)
        return []
    
    df = pd.DataFrame(successful)
    df = df.sort_values('score', ascending=False)
    
    # Get top N unique stocks
    portfolio = []
    seen = set()
    
    for _, row in df.iterrows():
        if row['stock'] not in seen and len(portfolio) < n:
            portfolio.append(row)
            seen.add(row['stock'])
    
    print("\n" + "="*100)
    print(f"PORTFOLIO ({n} STOCKS)")
    print("="*100)
    
    for stock in portfolio:
        alloc = stock['position_pct'] / n
        print(f"{stock['stock']:5} ({stock['stock_name']:<20}) {alloc:>5.1f}% | Score: {stock['score']:.0f} | 5th: {stock['fifth_percentile']:>6.1f}%")
    
    cash = 100 - sum(s['position_pct'] for s in portfolio) / n
    print(f"CASH  {'':26} {cash:>5.1f}%")
    
    avg_fifth = np.mean([s['fifth_percentile'] for s in portfolio])
    avg_median = np.mean([s['median_return'] for s in portfolio])
    
    print(f"\nPortfolio (simple avg): 5th: {avg_fifth:.2f}% | Median: {avg_median:.2f}%")
    
    return portfolio


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    results = screen_all()
    df = display_results(results)
    portfolio = build_portfolio(results, n=5)
    
    print("\n" + "="*100)
    print("DONE")
    print("="*100)
