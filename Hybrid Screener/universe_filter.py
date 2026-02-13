"""
Universe Filter Module
Filters stocks by volume, market cap, and ETF exclusion
"""
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def passes_universe_filter(ticker, min_volume, min_market_cap, include_etfs):
    """
    Check if ticker passes universe filter criteria
    
    Args:
        ticker: Stock symbol
        min_volume: Minimum average daily volume
        min_market_cap: Minimum market cap in USD
        include_etfs: Whether to include ETFs
        
    Returns:
        dict with 'passed' (bool) and 'reason' (str) keys
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check if ETF
        if not include_etfs:
            quote_type = info.get('quoteType', '')
            if quote_type == 'ETF':
                return {
                    'passed': False,
                    'reason': 'ETF excluded',
                    'volume': None,
                    'market_cap': None
                }
        
        # Get volume (average or current)
        volume = info.get('averageVolume10days') or info.get('averageVolume') or info.get('volume')
        if not volume or volume < min_volume:
            return {
                'passed': False,
                'reason': f'Volume too low ({volume:,} < {min_volume:,})',
                'volume': volume,
                'market_cap': None
            }
        
        # Get market cap
        market_cap = info.get('marketCap')
        if not market_cap or market_cap < min_market_cap:
            return {
                'passed': False,
                'reason': f'Market cap too low (${market_cap/1e9:.2f}B < ${min_market_cap/1e9:.2f}B)',
                'volume': volume,
                'market_cap': market_cap
            }
        
        return {
            'passed': True,
            'reason': 'Passed',
            'volume': volume,
            'market_cap': market_cap
        }
        
    except Exception as e:
        return {
            'passed': False,
            'reason': f'Error: {str(e)}',
            'volume': None,
            'market_cap': None
        }


def get_universe_data(ticker):
    """
    Get basic universe data for a ticker
    Returns dict with volume, market_cap, sector, industry
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'volume': info.get('averageVolume10days') or info.get('averageVolume'),
            'market_cap': info.get('marketCap'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'quote_type': info.get('quoteType', 'Unknown')
        }
    except:
        return {
            'volume': None,
            'market_cap': None,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'quote_type': 'Unknown'
        }