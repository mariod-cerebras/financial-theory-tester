#!/usr/bin/env python3
"""
Financial Theory Visualizer
Generate graphs showing buy/sell signals and theory explanations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

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


class FinancialTheoryVisualizer:
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
        
        # Try pandas-datareader first
        if PANDAS_DATAREADER_AVAILABLE:
            try:
                self.data = web.DataReader(
                    self.ticker, 
                    'stooq',
                    start=self.start_date,
                    end=self.end_date
                )
                if not self.data.empty:
                    self.data = self.data.sort_index()
                    print(f"✓ Fetched {len(self.data)} days of data")
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
                    print(f"✓ Fetched {len(self.data)} days of data")
                    return True
            except Exception as e:
                pass
        
        print(f"Error: No data found for {self.ticker}")
        return False

    def calculate_indicators(self):
        """Calculate all technical indicators"""
        if self.data is None:
            return
        
        prices = self.data['Close']
        
        # Moving averages
        self.data['SMA_50'] = prices.rolling(window=50).mean()
        self.data['SMA_200'] = prices.rolling(window=200).mean()
        
        # RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # Returns
        self.data['Returns'] = prices.pct_change()
        
        # Rolling mean and std for mean reversion
        self.data['Rolling_Mean'] = prices.rolling(window=20).mean()
        self.data['Rolling_Std'] = prices.rolling(window=20).std()
        self.data['Z_Score'] = (prices - self.data['Rolling_Mean']) / self.data['Rolling_Std']
        
        # Momentum
        self.data['Momentum_3M'] = prices.pct_change(63)
        self.data['Momentum_12M'] = prices.pct_change(252)

    def generate_buy_sell_signals(self):
        """Generate buy/sell signals based on theories"""
        if self.data is None:
            return
        
        self.data['Signal'] = 'HOLD'
        self.data['Signal_Reason'] = ''
        
        prices = self.data['Close']
        
        # Technical Analysis Signals
        golden_cross = (self.data['SMA_50'] > self.data['SMA_200']) & (self.data['SMA_50'].shift(1) <= self.data['SMA_200'].shift(1))
        death_cross = (self.data['SMA_50'] < self.data['SMA_200']) & (self.data['SMA_50'].shift(1) >= self.data['SMA_200'].shift(1))
        
        oversold = self.data['RSI'] < 30
        overbought = self.data['RSI'] > 70
        
        # Mean Reversion Signals
        extreme_high = self.data['Z_Score'] > 2
        extreme_low = self.data['Z_Score'] < -2
        
        # Momentum Signals
        positive_momentum = self.data['Momentum_3M'] > 0.05
        negative_momentum = self.data['Momentum_3M'] < -0.05
        
        # Generate signals
        for i in range(len(self.data)):
            if golden_cross.iloc[i]:
                self.data['Signal'].iloc[i] = 'BUY'
                self.data['Signal_Reason'].iloc[i] = 'Golden Cross'
            elif death_cross.iloc[i]:
                self.data['Signal'].iloc[i] = 'SELL'
                self.data['Signal_Reason'].iloc[i] = 'Death Cross'
            elif oversold.iloc[i]:
                self.data['Signal'].iloc[i] = 'BUY'
                self.data['Signal_Reason'].iloc[i] = 'RSI Oversold'
            elif overbought.iloc[i]:
                self.data['Signal'].iloc[i] = 'SELL'
                self.data['Signal_Reason'].iloc[i] = 'RSI Overbought'
            elif extreme_low.iloc[i]:
                self.data['Signal'].iloc[i] = 'BUY'
                self.data['Signal_Reason'].iloc[i] = 'Mean Reversion (Low)'
            elif extreme_high.iloc[i]:
                self.data['Signal'].iloc[i] = 'SELL'
                self.data['Signal_Reason'].iloc[i] = 'Mean Reversion (High)'

    def plot_price_with_signals(self):
        """Plot price with buy/sell signals"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Price chart
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=1, alpha=0.7)
        ax1.plot(self.data.index, self.data['SMA_50'], label='SMA 50', linewidth=1, alpha=0.6)
        ax1.plot(self.data.index, self.data['SMA_200'], label='SMA 200', linewidth=1, alpha=0.6)
        
        # Buy signals
        buy_signals = self.data[self.data['Signal'] == 'BUY']
        ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', s=100, label='BUY', zorder=5)
        
        # Sell signals
        sell_signals = self.data[self.data['Signal'] == 'SELL']
        ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', s=100, label='SELL', zorder=5)
        
        ax1.set_title(f'{self.ticker} Price with Buy/Sell Signals', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # RSI chart
        ax2.plot(self.data.index, self.data['RSI'], label='RSI', linewidth=1, color='purple')
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
        ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
        ax2.fill_between(self.data.index, 70, 100, alpha=0.1, color='red')
        ax2.fill_between(self.data.index, 0, 30, alpha=0.1, color='green')
        
        ax2.set_title('RSI Indicator', fontsize=14, fontweight='bold')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(f'{self.ticker}_price_signals.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved {self.ticker}_price_signals.png")
        plt.close()

    def plot_momentum_analysis(self):
        """Plot momentum analysis"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Momentum chart
        ax1.plot(self.data.index, self.data['Momentum_3M'] * 100, label='3-Month Momentum (%)', linewidth=1, color='blue')
        ax1.plot(self.data.index, self.data['Momentum_12M'] * 100, label='12-Month Momentum (%)', linewidth=1, color='orange')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.axhline(y=5, color='green', linestyle='--', alpha=0.5, label='Strong Momentum (5%)')
        ax1.axhline(y=-5, color='red', linestyle='--', alpha=0.5, label='Weak Momentum (-5%)')
        
        ax1.set_title(f'{self.ticker} Momentum Analysis', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Momentum (%)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Returns distribution
        returns = self.data['Returns'].dropna()
        ax2.hist(returns * 100, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(x=returns.mean() * 100, color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean()*100:.2f}%')
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        ax2.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Daily Return (%)', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.ticker}_momentum.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved {self.ticker}_momentum.png")
        plt.close()

    def plot_mean_reversion_analysis(self):
        """Plot mean reversion analysis"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Price with mean reversion bands
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=1, alpha=0.7)
        ax1.plot(self.data.index, self.data['Rolling_Mean'], label='20-Day Mean', linewidth=1, color='orange')
        ax1.fill_between(self.data.index, 
                        self.data['Rolling_Mean'] + 2 * self.data['Rolling_Std'],
                        self.data['Rolling_Mean'] - 2 * self.data['Rolling_Std'],
                        alpha=0.2, color='gray', label='±2 Std Dev')
        
        # Highlight extreme points
        extreme_high = self.data[self.data['Z_Score'] > 2]
        extreme_low = self.data[self.data['Z_Score'] < -2]
        
        ax1.scatter(extreme_high.index, extreme_high['Close'], color='red', marker='v', s=80, label='Extreme High', zorder=5)
        ax1.scatter(extreme_low.index, extreme_low['Close'], color='green', marker='^', s=80, label='Extreme Low', zorder=5)
        
        ax1.set_title(f'{self.ticker} Mean Reversion Analysis', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Z-Score chart
        ax2.plot(self.data.index, self.data['Z_Score'], label='Z-Score', linewidth=1, color='purple')
        ax2.axhline(y=2, color='red', linestyle='--', alpha=0.5, label='+2 Std Dev (Sell)')
        ax2.axhline(y=-2, color='green', linestyle='--', alpha=0.5, label='-2 Std Dev (Buy)')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.fill_between(self.data.index, 2, 4, alpha=0.1, color='red')
        ax2.fill_between(self.data.index, -4, -2, alpha=0.1, color='green')
        
        ax2.set_title('Z-Score (Price Deviation from Mean)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Z-Score', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.ticker}_mean_reversion.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved {self.ticker}_mean_reversion.png")
        plt.close()

    def plot_theory_summary(self):
        """Create a summary of all theories with visual explanations"""
        fig = plt.figure(figsize=(20, 12))
        
        # Create grid for subplots
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Efficient Market Hypothesis
        ax1 = fig.add_subplot(gs[0, 0])
        returns = self.data['Returns'].dropna()
        autocorr = returns.autocorr(lag=1)
        
        ax1.scatter(returns[:-1].values * 100, returns[1:].values * 100, alpha=0.5, s=10)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        # Add trend line
        z = np.polyfit(returns[:-1].values * 100, returns[1:].values * 100, 1)
        p = np.poly1d(z)
        ax1.plot(returns[:-1].values * 100, p(returns[:-1].values * 100), "r--", alpha=0.8, linewidth=2)
        
        emh_makes_sense = abs(autocorr) < 0.05
        sense_text = "✓ Makes Sense" if emh_makes_sense else "✗ Doesn't Make Sense"
        ax1.set_title(f'Efficient Market Hypothesis\nAutocorrelation: {autocorr:.4f}\n{sense_text}',
                     fontsize=12, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen" if emh_makes_sense else "lightcoral"))
        ax1.set_xlabel('Today\'s Return (%)', fontsize=10)
        ax1.set_ylabel('Tomorrow\'s Return (%)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 2. Momentum Theory
        ax2 = fig.add_subplot(gs[0, 1])
        monthly_returns = self.data['Close'].resample('ME').last().pct_change().dropna()
        
        if len(monthly_returns) >= 12:
            momentum_3m = monthly_returns.rolling(3).mean().shift(1)
            future_12m = monthly_returns.rolling(12).mean().shift(-1)
            momentum_corr = momentum_3m.corr(future_12m)
            
            ax2.scatter(momentum_3m.values * 100, future_12m.values * 100, alpha=0.5, s=30)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            momentum_makes_sense = momentum_corr > 0.1
            sense_text = "✓ Makes Sense" if momentum_makes_sense else "✗ Doesn't Make Sense"
            ax2.set_title(f'Momentum Theory\nCorrelation: {momentum_corr:.4f}\n{sense_text}',
                         fontsize=12, fontweight='bold',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen" if momentum_makes_sense else "lightcoral"))
            ax2.set_xlabel('Past 3-Month Return (%)', fontsize=10)
            ax2.set_ylabel('Future 12-Month Return (%)', fontsize=10)
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'Insufficient data\nfor momentum test', ha='center', va='center', fontsize=12)
            ax2.set_title('Momentum Theory', fontsize=12, fontweight='bold')
        
        # 3. Mean Reversion
        ax3 = fig.add_subplot(gs[1, 0])
        extreme_high = self.data['Z_Score'] > 2
        extreme_low = self.data['Z_Score'] < -2
        
        future_returns = self.data['Close'].pct_change(5).shift(-5)
        reversion_high = future_returns[extreme_high].mean() if extreme_high.any() else 0
        reversion_low = future_returns[extreme_low].mean() if extreme_low.any() else 0
        
        categories = ['After High\n(Z>2)', 'After Low\n(Z<-2)', 'Average']
        values = [reversion_high * 100, reversion_low * 100, returns.mean() * 100]
        colors = ['red' if reversion_high < 0 else 'green', 'green' if reversion_low > 0 else 'red', 'gray']
        
        bars = ax3.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        mean_reversion_makes_sense = (reversion_high < 0) and (reversion_low > 0)
        sense_text = "✓ Makes Sense" if mean_reversion_makes_sense else "✗ Doesn't Make Sense"
        ax3.set_title(f'Mean Reversion Theory\nHigh→{reversion_high*100:.2f}%, Low→{reversion_low*100:.2f}%\n{sense_text}',
                     fontsize=12, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen" if mean_reversion_makes_sense else "lightcoral"))
        ax3.set_ylabel('5-Day Forward Return (%)', fontsize=10)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Technical Analysis
        ax4 = fig.add_subplot(gs[1, 1])
        current_price = self.data['Close'].iloc[-1]
        sma_50 = self.data['SMA_50'].iloc[-1]
        sma_200 = self.data['SMA_200'].iloc[-1]
        current_rsi = self.data['RSI'].iloc[-1]
        
        golden_cross = sma_50 > sma_200
        price_above_mas = current_price > sma_50 and current_price > sma_200
        oversold = current_rsi < 30
        overbought = current_rsi > 70
        
        tech_makes_sense = price_above_mas and not overbought
        
        # Create technical indicators summary
        indicators = [
            f'Price: ${current_price:.2f}',
            f'SMA 50: ${sma_50:.2f}',
            f'SMA 200: ${sma_200:.2f}',
            f'RSI: {current_rsi:.2f}',
            f'Golden Cross: {"✓" if golden_cross else "✗"}',
            f'Price Above MAs: {"✓" if price_above_mas else "✗"}',
            f'Oversold: {"✓" if oversold else "✗"}',
            f'Overbought: {"✓" if overbought else "✗"}'
        ]
        
        ax4.axis('off')
        ax4.text(0.1, 0.9, 'Technical Analysis', fontsize=14, fontweight='bold', transform=ax4.transAxes)
        
        for i, indicator in enumerate(indicators):
            ax4.text(0.1, 0.8 - i*0.1, indicator, fontsize=11, transform=ax4.transAxes)
        
        interpretation = self._get_technical_interpretation(golden_cross, price_above_mas, oversold, overbought)
        sense_text = "✓ Makes Sense" if tech_makes_sense else "✗ Doesn't Make Sense"
        ax4.text(0.1, 0.1, f'Interpretation: {interpretation}\n{sense_text}',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen" if tech_makes_sense else "lightcoral"),
                transform=ax4.transAxes)
        
        # 5. Signal Performance
        ax5 = fig.add_subplot(gs[2, :])
        
        # Calculate signal performance
        buy_signals = self.data[self.data['Signal'] == 'BUY']
        sell_signals = self.data[self.data['Signal'] == 'SELL']
        
        ax5.text(0.5, 0.5, f'Buy Signals: {len(buy_signals)}\nSell Signals: {len(sell_signals)}\n\nSignal performance analysis\nrequires more data points\nfor accurate calculation.', 
                ha='center', va='center', fontsize=12)
        ax5.set_title('Signal Summary', fontsize=12, fontweight='bold')
        ax5.axis('off')
        
        plt.suptitle(f'{self.ticker} Financial Theory Analysis Summary', fontsize=16, fontweight='bold', y=0.995)
        plt.savefig(f'{self.ticker}_theory_summary.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved {self.ticker}_theory_summary.png")
        plt.close()

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

    def generate_all_visualizations(self):
        """Generate all visualizations"""
        if not self.fetch_data():
            return False
        
        self.calculate_indicators()
        self.generate_buy_sell_signals()
        
        print("\nGenerating visualizations...")
        self.plot_price_with_signals()
        self.plot_momentum_analysis()
        self.plot_mean_reversion_analysis()
        self.plot_theory_summary()
        
        print(f"\n✓ All visualizations generated for {self.ticker}!")
        print(f"  - {self.ticker}_price_signals.png")
        print(f"  - {self.ticker}_momentum.png")
        print(f"  - {self.ticker}_mean_reversion.png")
        print(f"  - {self.ticker}_theory_summary.png")
        
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python financial_theory_visualizer.py <TICKER> [period]")
        print("Example: python financial_theory_visualizer.py AAPL 2y")
        print("Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
        sys.exit(1)
    
    ticker = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else "2y"
    
    visualizer = FinancialTheoryVisualizer(ticker, period)
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()