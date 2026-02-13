"""
Regime Filter Module
Risk conditioning layer to suppress signals in unfavorable market conditions
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RegimeFilter:
    """
    Manages regime filters for risk conditioning
    """
    def __init__(self, config):
        self.config = config
        self.vix_level = None
        self.market_trend = None
        self.spy_above_ma = None
        
        if config.USE_REGIME_FILTERS:
            self._initialize_regime_data()
    
    def _initialize_regime_data(self):
        """Fetch regime data once at initialization"""
        
        # VIX filter
        if self.config.USE_VIX_FILTER:
            try:
                vix = yf.Ticker('^VIX')
                vix_data = vix.history(period='5d')
                if len(vix_data) > 0:
                    self.vix_level = vix_data['Close'].iloc[-1]
                    print(f"VIX Level: {self.vix_level:.2f}")
            except Exception as e:
                print(f"Warning: Could not fetch VIX data: {e}")
                self.vix_level = None
        
        # Market trend filter
        if self.config.USE_MARKET_TREND_FILTER:
            try:
                spy = yf.Ticker(self.config.MARKET_TREND_TICKER)
                
                # Get enough data for MA calculation
                lookback_days = int(self.config.MARKET_TREND_MA_PERIOD * 1.5)
                spy_data = spy.history(period=f'{lookback_days}d')
                
                if len(spy_data) >= self.config.MARKET_TREND_MA_PERIOD:
                    # Calculate moving average
                    ma = spy_data['Close'].rolling(window=self.config.MARKET_TREND_MA_PERIOD).mean()
                    current_price = spy_data['Close'].iloc[-1]
                    current_ma = ma.iloc[-1]
                    
                    self.spy_above_ma = current_price > current_ma
                    
                    trend = "BULLISH" if self.spy_above_ma else "BEARISH"
                    print(f"Market Trend ({self.config.MARKET_TREND_TICKER}): {trend}")
                    print(f"  Current: {current_price:.2f} | {self.config.MARKET_TREND_MA_PERIOD}MA: {current_ma:.2f}")
                else:
                    print(f"Warning: Insufficient data for {self.config.MARKET_TREND_MA_PERIOD}MA")
                    self.spy_above_ma = None
                    
            except Exception as e:
                print(f"Warning: Could not fetch market trend data: {e}")
                self.spy_above_ma = None
    
    def passes_regime_filter(self, signal_direction):
        """
        Check if signal passes regime filters
        
        Args:
            signal_direction: 'LONG' or 'SHORT'
            
        Returns:
            dict with 'passed' (bool), 'reason' (str), 'regime_flags' (dict)
        """
        if not self.config.USE_REGIME_FILTERS:
            return {
                'passed': True,
                'reason': 'Regime filters disabled',
                'regime_flags': {}
            }
        
        regime_flags = {}
        
        # VIX filter
        if self.config.USE_VIX_FILTER:
            if self.vix_level is not None:
                regime_flags['vix_level'] = self.vix_level
                regime_flags['vix_elevated'] = self.vix_level > self.config.MAX_VIX_THRESHOLD
                
                if self.vix_level > self.config.MAX_VIX_THRESHOLD:
                    return {
                        'passed': False,
                        'reason': f'VIX too high ({self.vix_level:.2f} > {self.config.MAX_VIX_THRESHOLD})',
                        'regime_flags': regime_flags
                    }
        
        # Market trend filter
        if self.config.USE_MARKET_TREND_FILTER:
            if self.spy_above_ma is not None:
                regime_flags['spy_above_ma'] = self.spy_above_ma
                regime_flags['market_trend'] = 'BULLISH' if self.spy_above_ma else 'BEARISH'
                
                # Long-only filter
                if self.config.MARKET_TREND_LONG_ONLY and signal_direction == 'LONG':
                    if not self.spy_above_ma:
                        return {
                            'passed': False,
                            'reason': 'Market trend bearish (long signals suppressed)',
                            'regime_flags': regime_flags
                        }
                
                # Short-only filter
                if self.config.MARKET_TREND_SHORT_ONLY and signal_direction == 'SHORT':
                    if self.spy_above_ma:
                        return {
                            'passed': False,
                            'reason': 'Market trend bullish (short signals suppressed)',
                            'regime_flags': regime_flags
                        }
        
        return {
            'passed': True,
            'reason': 'Passed all regime filters',
            'regime_flags': regime_flags
        }
    
    def get_regime_summary(self):
        """Return current regime state for reporting"""
        summary = {}
        
        if self.vix_level is not None:
            summary['VIX'] = f"{self.vix_level:.2f}"
        
        if self.spy_above_ma is not None:
            summary['Market Trend'] = 'BULLISH' if self.spy_above_ma else 'BEARISH'
        
        return summary