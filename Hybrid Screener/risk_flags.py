"""
Risk-Aware Output Module
Adds risk flags and cluster detection to results
"""
import pandas as pd
from collections import Counter

def add_risk_flags(results, config):
    """
    Add risk-aware flags to results
    
    Args:
        results: List of screening result dicts
        config: Configuration object
        
    Returns:
        List of results with added risk flags
    """
    if not results:
        return results
    
    df = pd.DataFrame(results)
    
    # 1. Sector concentration / cluster risk
    sector_counts = Counter(df['sector'].values)
    
    for i, result in enumerate(results):
        sector = result['sector']
        sector_count = sector_counts[sector]
        
        # Flag high concentration
        if sector_count >= config.SECTOR_CONCENTRATION_THRESHOLD:
            results[i]['cluster_risk'] = True
            results[i]['cluster_risk_note'] = f'{sector_count} signals in {sector}'
        else:
            results[i]['cluster_risk'] = False
            results[i]['cluster_risk_note'] = ''
    
    # 2. Elevated volatility regime
    vol_percentile_threshold = config.HIGH_VOL_PERCENTILE
    
    for i, result in enumerate(results):
        vol_pct = result.get('vol_percentile', 50)
        
        if vol_pct >= vol_percentile_threshold:
            results[i]['elevated_vol_regime'] = True
            results[i]['vol_regime_note'] = f'Vol at {vol_pct:.0f}th percentile'
        else:
            results[i]['elevated_vol_regime'] = False
            results[i]['vol_regime_note'] = ''
    
    return results


def generate_risk_summary(results, config):
    """
    Generate summary of risk flags
    
    Returns:
        dict with summary statistics
    """
    if not results:
        return {}
    
    df = pd.DataFrame(results)
    
    cluster_risk_count = df['cluster_risk'].sum() if 'cluster_risk' in df.columns else 0
    elevated_vol_count = df['elevated_vol_regime'].sum() if 'elevated_vol_regime' in df.columns else 0
    
    # Sector concentration
    sector_counts = Counter(df['sector'].values)
    concentrated_sectors = {
        sector: count for sector, count in sector_counts.items() 
        if count >= config.SECTOR_CONCENTRATION_THRESHOLD
    }
    
    return {
        'total_signals': len(results),
        'cluster_risk_signals': cluster_risk_count,
        'elevated_vol_signals': elevated_vol_count,
        'concentrated_sectors': concentrated_sectors,
        'long_signals': (df['signal'] == 'LONG').sum(),
        'short_signals': (df['signal'] == 'SHORT').sum()
    }


def print_risk_summary(risk_summary):
    """Print formatted risk summary"""
    print("\n" + "="*80)
    print("RISK SUMMARY")
    print("="*80)
    
    print(f"\nTotal Signals: {risk_summary['total_signals']}")
    print(f"  Long:  {risk_summary['long_signals']}")
    print(f"  Short: {risk_summary['short_signals']}")
    
    print(f"\nRisk Flags:")
    print(f"  Cluster Risk: {risk_summary['cluster_risk_signals']} signals")
    print(f"  Elevated Volatility: {risk_summary['elevated_vol_signals']} signals")
    
    if risk_summary['concentrated_sectors']:
        print(f"\nSector Concentration:")
        for sector, count in risk_summary['concentrated_sectors'].items():
            print(f"  {sector}: {count} signals")