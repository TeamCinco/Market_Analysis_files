"""
Fundamental Survivability Filter
Filters stocks by valuation metrics to avoid structurally broken companies
NOT USED FOR TIMING - ONLY AS A FILTER
"""
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_fundamental_metrics(ticker):
    """
    Extract fundamental metrics for a stock
    
    Returns:
        dict with PE, forward_PE, EV_EBITDA, FCF_yield, sector
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # P/E ratios
        pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        
        # EV/EBITDA
        ev_ebitda = info.get('enterpriseToEbitda')
        
        # FCF Yield (calculated as FCF / Market Cap)
        fcf = info.get('freeCashflow')
        market_cap = info.get('marketCap')
        fcf_yield = (fcf / market_cap) if (fcf and market_cap and market_cap > 0) else None
        
        # Sector
        sector = info.get('sector', 'Unknown')
        
        return {
            'pe': pe,
            'forward_pe': forward_pe,
            'ev_ebitda': ev_ebitda,
            'fcf_yield': fcf_yield,
            'sector': sector,
            'success': True
        }
        
    except Exception as e:
        return {
            'pe': None,
            'forward_pe': None,
            'ev_ebitda': None,
            'fcf_yield': None,
            'sector': 'Unknown',
            'success': False,
            'error': str(e)
        }


def calculate_sector_percentiles(tickers, config):
    """
    Calculate sector-wise P/E percentiles
    This should be run once at the start for all tickers
    
    Returns:
        dict: {sector: {median_pe, median_forward_pe, ...}}
    """
    print("\nCalculating sector percentiles...")
    
    sector_data = {}
    
    for ticker in tickers:
        try:
            metrics = get_fundamental_metrics(ticker)
            if metrics['success'] and metrics['sector'] != 'Unknown':
                sector = metrics['sector']
                
                if sector not in sector_data:
                    sector_data[sector] = {
                        'pe_values': [],
                        'forward_pe_values': []
                    }
                
                if metrics['pe'] and metrics['pe'] > 0:
                    sector_data[sector]['pe_values'].append(metrics['pe'])
                
                if metrics['forward_pe'] and metrics['forward_pe'] > 0:
                    sector_data[sector]['forward_pe_values'].append(metrics['forward_pe'])
        except:
            continue
    
    # Calculate percentiles
    sector_percentiles = {}
    
    for sector, data in sector_data.items():
        sector_percentiles[sector] = {}
        
        if data['pe_values']:
            sector_percentiles[sector]['median_pe'] = np.percentile(data['pe_values'], 50)
            sector_percentiles[sector]['pe_percentile_threshold'] = np.percentile(
                data['pe_values'], 
                config.PE_PERCENTILE_THRESHOLD
            )
        
        if data['forward_pe_values']:
            sector_percentiles[sector]['median_forward_pe'] = np.percentile(data['forward_pe_values'], 50)
            sector_percentiles[sector]['forward_pe_percentile_threshold'] = np.percentile(
                data['forward_pe_values'],
                config.FORWARD_PE_PERCENTILE_THRESHOLD
            )
    
    print(f"Calculated percentiles for {len(sector_percentiles)} sectors")
    return sector_percentiles


def passes_fundamental_filter(ticker, sector_percentiles, config):
    """
    Check if stock passes fundamental survivability filters
    
    Returns:
        dict with 'passed' (bool), 'reason' (str), and metrics
    """
    metrics = get_fundamental_metrics(ticker)
    
    if not metrics['success']:
        return {
            'passed': False,
            'reason': 'Could not fetch fundamentals',
            'metrics': metrics
        }
    
    sector = metrics['sector']
    pe = metrics['pe']
    forward_pe = metrics['forward_pe']
    
    # Exclude negative P/E if configured
    if config.EXCLUDE_NEGATIVE_PE and pe and pe < 0:
        return {
            'passed': False,
            'reason': f'Negative P/E ({pe:.2f})',
            'metrics': metrics
        }
    
    # P/E filtering
    if config.USE_SECTOR_MEDIAN_PE:
        # Compare to sector percentile
        if sector in sector_percentiles and pe:
            threshold = sector_percentiles[sector].get('pe_percentile_threshold')
            sector_median = sector_percentiles[sector].get('median_pe')
            
            if threshold and pe > threshold:
                return {
                    'passed': False,
                    'reason': f'P/E too high vs sector ({pe:.2f} > {threshold:.2f})',
                    'metrics': metrics,
                    'sector_median_pe': sector_median
                }
        elif pe:
            # No sector data, fallback to absolute threshold
            if pe > config.ABSOLUTE_PE_MAX:
                return {
                    'passed': False,
                    'reason': f'P/E too high ({pe:.2f} > {config.ABSOLUTE_PE_MAX})',
                    'metrics': metrics,
                    'sector_median_pe': None
                }
    else:
        # Use absolute P/E threshold
        if pe and pe > config.ABSOLUTE_PE_MAX:
            return {
                'passed': False,
                'reason': f'P/E too high ({pe:.2f} > {config.ABSOLUTE_PE_MAX})',
                'metrics': metrics,
                'sector_median_pe': None
            }
    
    # Forward P/E filtering (if enabled and available)
    if config.USE_FORWARD_PE and forward_pe:
        if config.USE_SECTOR_MEDIAN_PE and sector in sector_percentiles:
            threshold = sector_percentiles[sector].get('forward_pe_percentile_threshold')
            if threshold and forward_pe > threshold:
                return {
                    'passed': False,
                    'reason': f'Forward P/E too high vs sector ({forward_pe:.2f} > {threshold:.2f})',
                    'metrics': metrics,
                    'sector_median_pe': sector_percentiles[sector].get('median_pe')
                }
    
    # EV/EBITDA filter (if enabled)
    if config.USE_EV_EBITDA:
        ev_ebitda = metrics['ev_ebitda']
        if ev_ebitda and ev_ebitda > config.EV_EBITDA_THRESHOLD:
            return {
                'passed': False,
                'reason': f'EV/EBITDA too high ({ev_ebitda:.2f} > {config.EV_EBITDA_THRESHOLD})',
                'metrics': metrics,
                'sector_median_pe': sector_percentiles.get(sector, {}).get('median_pe')
            }
    
    # FCF Yield filter (if enabled)
    if config.USE_FCF_YIELD:
        fcf_yield = metrics['fcf_yield']
        if not fcf_yield or fcf_yield < config.MIN_FCF_YIELD:
            return {
                'passed': False,
                'reason': f'FCF yield too low ({fcf_yield:.2%} < {config.MIN_FCF_YIELD:.2%})' if fcf_yield else 'No FCF data',
                'metrics': metrics,
                'sector_median_pe': sector_percentiles.get(sector, {}).get('median_pe')
            }
    
    # Passed all filters
    sector_median = sector_percentiles.get(sector, {}).get('median_pe')
    
    return {
        'passed': True,
        'reason': 'Passed fundamental filters',
        'metrics': metrics,
        'sector_median_pe': sector_median
    }