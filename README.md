# Financial Strategy Backtester

Test your trading strategies against 5 years of historical data. Pick any ticker, describe your strategy in plain English, and see exactly where your money would have taken you.

## Quick Start

```bash
python3 strategy_backtester.py <TICKER> "<YOUR STRATEGY>"
```

## Examples

**Buy on dips, sell on rises:**

```bash
python3 strategy_backtester.py AAPL "Buy when it dips 10%, sell when it rises 10%"
```

**Price-based strategy:**

```bash
python3 strategy_backtester.py NVDA "Buy below 100, sell above 150"
```

**RSI-based strategy:**

```bash
python3 strategy_backtester.py TSLA "Buy when RSI below 30, sell when RSI above 70"
```

**Flexible language:**

```bash
python3 strategy_backtester.py MSFT "Buy when price falls 5%, sell when it increases 8%"
python3 strategy_backtester.py AAPL "Buy when it declines 7.5%, sell when it gains 12%"
```

## How It Works

1. **Parse Strategy**: Converts your natural language description into executable rules
2. **Fetch Data**: Downloads 5 years of historical stock data
3. **Run Simulation**: Iterates through historical data, executing trades when conditions are met
4. **Calculate Performance**: Tracks portfolio value, returns, and trade statistics
5. **Generate Visualization**: Creates comprehensive charts showing results
6. **Auto-Open**: Automatically displays the chart for analysis

## Output

The backtester generates a visualization with two panels:

**Top Panel - Stock Price with Trades:**

- Historical stock price chart
- Green triangles (▲) = BUY signals
- Red triangles (▼) = SELL signals
- Trade markers with dates and prices

**Bottom Panel - Portfolio Performance:**

- Portfolio value over time
- Initial capital reference line
- Final portfolio value
- Total return percentage
- Color-coded performance (green = profit, red = loss)

Charts automatically open in your default image viewer.

## Supported Strategy Types

### Price Dip Strategies

- "Buy when it dips 10%"
- "Buy when price drops 5%"
- "Buy when it falls 7.5%"
- "Buy when it declines 10 percent"

### Price Target Strategies

- "Buy below 100, sell above 120"
- "Buy below $50, sell above $75"

### RSI Strategies

- "Buy when RSI below 30, sell when RSI above 70"
- "Buy when RSI below 25"

### Percentage Gain Strategies

- "Buy when it dips 10%, sell when it rises 15%"
- "Buy when price drops 5%, sell when it gains 8%"
- "Buy when it falls 7%, sell when it increases 12%"
- "Buy when it declines 5%, sell when it profits 10%"

### Flexible Language Options

The parser understands various ways to express the same concept:

**For price drops:** dips, drops, falls, declines

**For price increases:** rises, gains, increases, profits

**For percentages:** 5%, 5 percent, 7.5%, 7.5 percent

**For capital:** with $10000, with 10000 initial capital, invest $10000

### Custom Initial Capital

Include your starting capital in the strategy:

```bash
python3 strategy_backtester.py AAPL "Buy when it dips 10% with $50000"
python3 strategy_backtester.py NVDA "Buy below 100, sell above 150 invest $25000"
```

## Installation

```bash
python3 -m pip install pandas numpy pandas-datareader yfinance matplotlib
```

## Real Results

**Strategy**: "Buy when it dips 10%, sell when it rises 10%"
**Stock**: AAPL
**Result**: +152.46% return over 5 years (18 trades)

**Strategy**: "Buy below 100, sell above 150"
**Stock**: NVDA
**Result**: +1086.73% return over 5 years (2 trades)

**Strategy**: "Buy when RSI below 30, sell when RSI above 70"
**Stock**: TSLA
**Result**: +157.34% return over 5 years (35 trades)

> "Knowledge applied to markets compounds faster than capital."

## Technical Details

- **Runtime**: Python 3.9+ with pandas, numpy, matplotlib
- **Data Sources**: pandas-datareader (Stooq), yfinance (fallback)
- **Data Period**: 5 years of historical data
- **Visualization**: High-resolution PNG (300 DPI)
- **Position Sizing**: Maximum shares affordable with available cash

## Notes

- Strategies are backtested on historical data - past performance doesn't guarantee future results
- Some strategies may not trigger if conditions are never met
- Charts are saved as PNG files in the current directory
- Transaction costs and slippage are not included in simulations

## Advanced Features

For deeper analysis, test established financial theories:

```bash
python3 financial_theory_visualizer.py <TICKER> [period]
```

Tests include:

- Efficient Market Hypothesis
- Momentum Theory
- Mean Reversion
- Value Investing
- Technical Analysis

> "The market rewards those who do the work."
