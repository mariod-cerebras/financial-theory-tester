#!/usr/bin/env python3
"""
Financial Theory Tester
Test financial theories on stocks of your choice
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys

try:
    import pandas_datareader.data as web
    PANDAS_DATAREADER_AVAILABLE = True
except ImportError:
    PANDAS_DATAREADER_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class FinancialTheoryTester:
    def __init__(self, ticker: str, period: str = "2y"):
        self.ticker = ticker.upper()
        self.period = period
        self.data = None
        self.info = {}
        
        # Convert period to dates
        self.end_date = datetime.now()
        if period == "1d":
            self.start_date = self.end_date - timedelta(days=1)
        elif period == "5d":
            self.start_date = self.end_date - timedelta(days=5)
        elif period == "1mo":
            self.start_date = self.end_date - timedelta(days=30)
        elif period == "3mo":
            self.start_date = self.end_date - timedelta(days=90)
        elif period == "6mo":
            self.start_date = self.end_date - timedelta(days=180)
        elif period == "1y":
            self.start_date = self.end_date - timedelta(days=365)
        elif period == "2y":
            self.start_date = self.end_date - timedelta(days=730)
        elif period == "5y":
            self.start_date = self.end_date - timedelta(days=1825)
        elif period == "10y":
            self.start_date = self.end_date - timedelta(days=3650)
        elif period == "ytd":
            self.start_date = datetime(self.end_date.year, 1, 1)
        else:
            self.start_date = self.end_date - timedelta(days=730)

    def fetch_data(self):
        """Fetch historical data for the stock"""
        print(f"Fetching data for {self.ticker}...")
        
        # Try pandas-datareader first (more reliable)
        if PANDAS_DATAREADER_AVAILABLE:
            try:
                self.data = web.DataReader(
                    self.ticker, 
                    'stooq',
                    start=self.start_date,
                    end=self.end_date
                )
                if not self.data.empty:
                    # Stooq returns data in reverse order
                    self.data = self.data.sort_index()
                    print(f"✓ Fetched {len(self.data)} days of data using pandas-datareader")
                    return True
            except Exception as e:
                pass
        
        # Try yfinance as fallback
        if YFINANCE_AVAILABLE:
            try:
                stock = yf.Ticker(self.ticker)
                self.data = stock.history(period=self.period)
                if not self.data.empty:
                    try:
                        self.info = stock.info
                    except:
                        self.info = {}
                    print(f"✓ Fetched {len(self.data)} days of data using yfinance")
                    return True
            except Exception as e:
                pass
        
        print(f"Error: No data found for {self.ticker}")
        return False

    def test_efficient_market_hypothesis(self) -> Dict:
        """Test if stock follows random walk (EMH)"""
        if self.data is None:
            return {"error": "No data available"}

        returns = self.data['Close'].pct_change().dropna()
        
        # Calculate autocorrelation
        autocorr = returns.autocorr(lag=1)
        
        # Run test for random walk
        # If returns are truly random, autocorrelation should be near 0
        is_random_walk = abs(autocorr) < 0.05
        
        return {
            "theory": "Efficient Market Hypothesis",
            "autocorrelation": round(autocorr, 4),
            "is_random_walk": is_random_walk,
            "interpretation": "Stock follows random walk" if is_random_walk else "Stock shows momentum/reversal patterns",
            "makes_sense": is_random_walk
        }

    def test_momentum_theory(self) -> Dict:
        """Test momentum strategy - past winners continue to win"""
        if self.data is None:
            return {"error": "No data available"}

        # Calculate 3-month and 12-month returns
        monthly_returns = self.data['Close'].resample('M').last().pct_change().dropna()
        
        if len(monthly_returns) < 12:
            return {"error": "Insufficient data for momentum test"}

        # Test if positive 3-month returns predict positive 12-month returns
        momentum_3m = monthly_returns.rolling(3).mean().shift(1)
        future_12m = monthly_returns.rolling(12).mean().shift(-1)
        
        # Calculate correlation
        momentum_corr = momentum_3m.corr(future_12m)
        
        has_momentum = momentum_corr > 0.1
        
        return {
            "theory": "Momentum Theory",
            "momentum_correlation": round(momentum_corr, 4),
            "has_momentum": has_momentum,
            "interpretation": "Stock shows momentum patterns" if has_momentum else "No clear momentum pattern",
            "makes_sense": has_momentum
        }

    def test_mean_reversion(self) -> Dict:
        """Test if stock reverts to mean"""
        if self.data is None:
            return {"error": "No data available"}

        prices = self.data['Close']
        
        # Calculate rolling mean and std
        rolling_mean = prices.rolling(window=20).mean()
        rolling_std = prices.rolling(window=20).std()
        
        # Calculate z-scores
        z_scores = (prices - rolling_mean) / rolling_std
        
        # Count how often extreme z-scores revert
        extreme_high = z_scores > 2
        extreme_low = z_scores < -2
        
        # Check if prices revert after extreme moves
        future_returns = prices.pct_change(5).shift(-5)
        
        reversion_high = future_returns[extreme_high].mean() if extreme_high.any() else 0
        reversion_low = future_returns[extreme_low].mean() if extreme_low.any() else 0
        
        # Mean reversion exists if extreme highs lead to negative returns
        # and extreme lows lead to positive returns
        shows_reversion = (reversion_high < 0) and (reversion_low > 0)
        
        return {
            "theory": "Mean Reversion",
            "reversion_after_high": round(reversion_high, 4),
            "reversion_after_low": round(reversion_low, 4),
            "shows_reversion": shows_reversion,
            "interpretation": "Stock shows mean reversion" if shows_reversion else "No clear mean reversion",
            "makes_sense": shows_reversion
        }

    def test_value_investing(self) -> Dict:
        """Test if low P/E stocks outperform"""
        pe_ratio = self.info.get('forwardPE', None)
        pb_ratio = self.info.get('priceToBook', None)
        
        if pe_ratio is None:
            return {"error": "P/E ratio not available"}

        # Simple value test: P/E < 15 is considered value
        is_value_stock = pe_ratio < 15
        
        # Check if stock has been performing well
        if self.data is not None and len(self.data) > 252:
            annual_return = (self.data['Close'].iloc[-1] / self.data['Close'].iloc[0]) - 1
            value_works = is_value_stock and annual_return > 0.10
        else:
            value_works = is_value_stock
        
        return {
            "theory": "Value Investing",
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "pb_ratio": round(pb_ratio, 2) if pb_ratio else None,
            "is_value_stock": is_value_stock,
            "interpretation": "Stock appears undervalued" if is_value_stock else "Stock appears overvalued",
            "makes_sense": value_works
        }

    def test_technical_analysis(self) -> Dict:
        """Test basic technical indicators"""
        if self.data is None:
            return {"error": "No data available"}

        prices = self.data['Close']
        
        # Calculate moving averages
        sma_50_series = prices.rolling(window=50).mean()
        sma_200_series = prices.rolling(window=200).mean()
        sma_50 = 0.0
        sma_200 = 0.0
        try:
            sma_50 = float(sma_50_series.iloc[-1])  # type: ignore
        except (IndexError, KeyError):
            pass
        try:
            sma_200 = float(sma_200_series.iloc[-1])  # type: ignore
        except (IndexError, KeyError):
            pass
        current_price = float(prices.iloc[-1])  # type: ignore
        
        # Golden cross: 50-day MA above 200-day MA
        golden_cross = sma_50 > sma_200
        
        # Price above both MAs
        price_above_mas = current_price > sma_50 and current_price > sma_200
        
        # RSI calculation
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = 50.0
        try:
            current_rsi = float(rsi.iloc[-1])  # type: ignore
        except (IndexError, KeyError):
            pass
        
        # RSI signals
        oversold = current_rsi < 30
        overbought = current_rsi > 70
        
        return {
            "theory": "Technical Analysis",
            "current_price": round(current_price, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2),
            "golden_cross": golden_cross,
            "price_above_mas": price_above_mas,
            "rsi": round(current_rsi, 2),
            "oversold": oversold,
            "overbought": overbought,
            "interpretation": self._get_technical_interpretation(golden_cross, price_above_mas, oversold, overbought),
            "makes_sense": price_above_mas and not overbought
        }

    def _get_technical_interpretation(self, golden_cross, price_above_mas, oversold, overbought):
        if oversold:
            return "Oversold - potential buy signal"
        if overbought:
            return "Overbought - potential sell signal"
        if golden_cross and price_above_mas:
            return "Bullish trend - golden cross"
        if not golden_cross and not price_above_mas:
            return "Bearish trend - below MAs"
        return "Neutral technical position"

    def run_all_tests(self) -> List[Dict]:
        """Run all financial theory tests"""
        if not self.fetch_data():
            return []

        tests = [
            self.test_efficient_market_hypothesis(),
            self.test_momentum_theory(),
            self.test_mean_reversion(),
            self.test_value_investing(),
            self.test_technical_analysis()
        ]
        
        return [t for t in tests if "error" not in t]

    def print_results(self):
        """Print formatted results"""
        print(f"\n{'='*60}")
        print(f"FINANCIAL THEORY TEST RESULTS: {self.ticker}")
        print(f"{'='*60}\n")
        
        tests = self.run_all_tests()
        
        if not tests:
            print("No tests could be run")
            return
        
        for test in tests:
            print(f"📊 {test['theory']}")
            print(f"   Interpretation: {test['interpretation']}")
            print(f"   Makes Sense: {'✓ Yes' if test['makes_sense'] else '✗ No'}")
            print()
        
        # Summary
        makes_sense_count = sum(1 for t in tests if t['makes_sense'])
        total_tests = len(tests)
        
        print(f"{'='*60}")
        print(f"SUMMARY: {makes_sense_count}/{total_tests} theories make sense for {self.ticker}")
        print(f"{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python financial_theory_tester.py <TICKER> [period]")
        print("Example: python financial_theory_tester.py AAPL 2y")
        print("Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
        sys.exit(1)
    
    ticker = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else "2y"
    
    tester = FinancialTheoryTester(ticker, period)
    tester.print_results()


if __name__ == "__main__":
    main()