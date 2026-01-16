#!/usr/bin/env python3
"""
Strategy Backtester - Simulate user-defined trading strategies and visualize results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sys
import re
import subprocess
import os

def get_stock_data(ticker, period='5y'):
    """Fetch stock data using pandas-datareader"""
    try:
        import pandas_datareader.data as web
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*5)
        
        df = web.DataReader(ticker, 'stooq', start_date, end_date)
        df = df.sort_index()
        return df
    except Exception as e:
        print(f"Error fetching data with pandas-datareader: {e}")
        try:
            import yfinance as yf
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period=period)
            return df
        except Exception as e2:
            print(f"Error fetching data with yfinance: {e2}")
            return None

def parse_strategy(strategy_text):
    """Parse user strategy into executable rules
    
    NOTE: Ideally this would use LLM text-to-code conversion for more flexible
    natural language understanding, but for the sake of time and simplicity,
    regex-based parsing is used here. This could be enhanced with an LLM API
    call to convert arbitrary strategy descriptions into executable code.
    """
    strategy = {
        'buy_conditions': [],
        'sell_conditions': [],
        'initial_capital': 10000,
        'description': strategy_text
    }
    
    strategy_text = strategy_text.lower()
    
    # Helper function to extract percentage
    def extract_percentage(text):
        match = re.search(r'(\d+\.?\d*)\s*[%]|(\d+\.?\d*)\s*percent', text)
        if match:
            return float(match.group(1) or match.group(2))
        return None
    
    # Parse buy conditions
    if 'dip' in strategy_text or 'drop' in strategy_text or 'fall' in strategy_text or 'decline' in strategy_text:
        dip_percent = extract_percentage(strategy_text)
        if dip_percent:
            strategy['buy_conditions'].append({
                'type': 'dip',
                'percent': dip_percent
            })
    
    if 'rsi' in strategy_text and 'below' in strategy_text:
        rsi_index = strategy_text.lower().find('rsi')
        below_index = strategy_text.lower().find('below')
        if rsi_index < below_index:
            match = re.search(r'rsi.*below\s*(\d+)', strategy_text)
            if match:
                rsi_value = float(match.group(1))
                strategy['buy_conditions'].append({
                    'type': 'rsi_below',
                    'value': rsi_value
                })
    
    if 'below' in strategy_text and ('rsi' not in strategy_text or strategy_text.lower().find('rsi') > strategy_text.lower().find('below')):
        match = re.search(r'below\s*[\$\\\$]?(\d+\.?\d*)', strategy_text)
        if match:
            price = float(match.group(1))
            strategy['buy_conditions'].append({
                'type': 'price_below',
                'price': price
            })
    
    # Parse sell conditions
    if 'rise' in strategy_text or 'gain' in strategy_text or 'increase' in strategy_text or 'profit' in strategy_text:
        rise_percent = extract_percentage(strategy_text)
        if rise_percent:
            strategy['sell_conditions'].append({
                'type': 'rise',
                'percent': rise_percent
            })
    
    if 'rsi' in strategy_text and 'above' in strategy_text:
        match = re.search(r'rsi.*above\s*(\d+)', strategy_text)
        if match:
            rsi_value = float(match.group(1))
            strategy['sell_conditions'].append({
                'type': 'rsi_above',
                'value': rsi_value
            })
    
    if 'above' in strategy_text and 'rsi' not in strategy_text.lower().split('above')[0]:
        match = re.search(r'above\s*[\$\\\$]?(\d+\.?\d*)', strategy_text)
        if match:
            price = float(match.group(1))
            strategy['sell_conditions'].append({
                'type': 'price_above',
                'price': price
            })
    
    # Parse initial capital
    match = re.search(r'\$?(\d+\.?\d*)\s*(?:initial|starting|capital|money|with|invest)', strategy_text)
    if match:
        strategy['initial_capital'] = float(match.group(1))
    
    return strategy

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_buy_conditions(df, index, strategy, rolling_window=20):
    """Check if buy conditions are met"""
    current_price = df.loc[index, 'Close']
    
    for condition in strategy['buy_conditions']:
        if condition['type'] == 'dip':
            # Calculate how much price has dropped from recent high
            recent_high = df.loc[:index, 'Close'].rolling(window=rolling_window).max().iloc[-1]
            drop_percent = ((recent_high - current_price) / recent_high) * 100
            if drop_percent >= condition['percent']:
                return True, f"Price dropped {drop_percent:.1f}% from recent high"
        
        elif condition['type'] == 'price_below':
            if current_price < condition['price']:
                return True, f"Price ${current_price:.2f} below ${condition['price']}"
        
        elif condition['type'] == 'rsi_below':
            rsi = calculate_rsi(df.loc[:index, 'Close'])
            current_rsi = rsi.iloc[-1]
            if current_rsi < condition['value']:
                return True, f"RSI {current_rsi:.1f} below {condition['value']}"
    
    return False, None

def check_sell_conditions(df, index, strategy, entry_price):
    """Check if sell conditions are met"""
    current_price = df.loc[index, 'Close']
    
    for condition in strategy['sell_conditions']:
        if condition['type'] == 'rise':
            gain_percent = ((current_price - entry_price) / entry_price) * 100
            if gain_percent >= condition['percent']:
                return True, f"Price rose {gain_percent:.1f}% from entry"
        
        elif condition['type'] == 'price_above':
            if current_price > condition['price']:
                return True, f"Price ${current_price:.2f} above ${condition['price']}"
        
        elif condition['type'] == 'rsi_above':
            rsi = calculate_rsi(df.loc[:index, 'Close'])
            current_rsi = rsi.iloc[-1]
            if current_rsi > condition['value']:
                return True, f"RSI {current_rsi:.1f} above {condition['value']}"
    
    return False, None

def backtest_strategy(df, strategy):
    """Run backtest simulation"""
    cash = strategy['initial_capital']
    shares = 0
    portfolio_value = []
    trades = []
    in_position = False
    entry_price = 0
    
    for i, (date, row) in enumerate(df.iterrows()):
        current_price = row['Close']
        
        if not in_position:
            should_buy, reason = check_buy_conditions(df, date, strategy)
            if should_buy:
                shares = int(cash / current_price)
                cash = cash - (shares * current_price)
                entry_price = current_price
                in_position = True
                trades.append({
                    'date': date,
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'reason': reason
                })
        else:
            should_sell, reason = check_sell_conditions(df, date, strategy, entry_price)
            if should_sell:
                cash = cash + (shares * current_price)
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': current_price,
                    'shares': shares,
                    'reason': reason
                })
                shares = 0
                in_position = False
        
        portfolio_value.append(cash + (shares * current_price))
    
    final_value = portfolio_value[-1]
    total_return = ((final_value - strategy['initial_capital']) / strategy['initial_capital']) * 100
    
    return portfolio_value, trades, final_value, total_return

def plot_backtest_results(df, portfolio_value, trades, ticker, strategy):
    """Plot stock price and portfolio value"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Stock Price with Trades
    ax1.plot(df.index, df['Close'], label='Stock Price', color='blue', linewidth=1)
    
    buy_trades = [t for t in trades if t['type'] == 'BUY']
    sell_trades = [t for t in trades if t['type'] == 'SELL']
    
    if buy_trades:
        buy_dates = [t['date'] for t in buy_trades]
        buy_prices = [t['price'] for t in buy_trades]
        ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='Buy', zorder=5)
    
    if sell_trades:
        sell_dates = [t['date'] for t in sell_trades]
        sell_prices = [t['price'] for t in sell_trades]
        ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='Sell', zorder=5)
    
    ax1.set_title(f'{ticker} Stock Price - Strategy: {strategy["description"][:50]}...', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Portfolio Value
    ax2.plot(df.index, portfolio_value, label='Portfolio Value', color='purple', linewidth=2)
    ax2.axhline(y=strategy['initial_capital'], color='gray', linestyle='--', label=f'Initial Capital (${strategy["initial_capital"]:,.0f})')
    
    final_value = portfolio_value[-1]
    total_return = ((final_value - strategy['initial_capital']) / strategy['initial_capital']) * 100
    color = 'green' if total_return >= 0 else 'red'
    ax2.text(0.02, 0.95, f'Final: ${final_value:,.2f}\nReturn: {total_return:+.2f}%', 
             transform=ax2.transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=color, alpha=0.1))
    
    ax2.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    filename = f'{ticker}_strategy_backtest.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    return filename

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 strategy_backtester.py <TICKER> <STRATEGY>")
        print("\nExample strategies:")
        print("  'Buy when it dips 10 percent'")
        print("  'Buy when RSI below 30, sell when RSI above 70'")
        print("  'Buy when price drops 5 percent, sell when it rises 10 percent'")
        print("  'Buy below 100, sell above 120'")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    strategy_text = ' '.join(sys.argv[2:])
    
    df = get_stock_data(ticker)
    
    if df is None or df.empty:
        print(f"Error: Could not fetch data for {ticker}")
        sys.exit(1)
    
    strategy = parse_strategy(strategy_text)
    portfolio_value, trades, final_value, total_return = backtest_strategy(df, strategy)
    filename = plot_backtest_results(df, portfolio_value, trades, ticker, strategy)
    
    if filename and os.path.exists(filename):
        try:
            subprocess.run(['open', filename], check=True)
        except Exception as e:
            print(f"Could not open chart: {e}")

if __name__ == '__main__':
    main()