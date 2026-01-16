# Financial Strategy Backtester

Backtest your trading strategies on historical stock data with automatic visualization. Test any strategy you can describe in plain English and see how it would have performed.

## Features

- **Natural Language Strategy Parsing**: Describe your strategy in plain English
- **Historical Backtesting**: Simulate trades on up to 5 years of historical data
- **Automatic Visualization**: Generate comprehensive charts showing performance
- **Multiple Strategy Types**: Support for price-based, percentage-based, and RSI-based strategies
- **Instant Results**: Charts automatically open after analysis

## Installation

Install Python dependencies:

```bash
python3 -m pip install pandas numpy pandas-datareader yfinance matplotlib
```

## Usage

### Strategy Backtesting (Primary Feature)

```bash
python3 strategy_backtester.py <TICKER> "<STRATEGY>"
```

### Examples

**Buy on dips, sell on rises:**

```bash
python3 strategy_backtester.py AAPL "Buy when it dips 10 percent, sell when it rises 10 percent"
```

**Price-based strategy:**

```bash
python3 strategy_backtester.py NVDA "Buy below 100, sell above 150"
```

**RSI-based strategy:**

```bash
python3 strategy_backtester.py TSLA "Buy when RSI below 30, sell when RSI above 70"
```

**Combined strategy:**

```bash
python3 strategy_backtester.py MSFT "Buy when it dips 5 percent, sell when it rises 8 percent"
```

## Supported Strategy Types

### Price Dip Strategies

- "Buy when it dips 10 percent"
- "Buy when price drops 5 percent"

### Price Target Strategies

- "Buy below 100, sell above 120"
- "Buy below $50, sell above $75"

### RSI Strategies

- "Buy when RSI below 30, sell when RSI above 70"
- "Buy when RSI below 25"

### Percentage Gain Strategies

- "Buy when it dips 10 percent, sell when it rises 15 percent"
- "Buy when price drops 5 percent, sell when it gains 8 percent"

### Combined Strategies

Mix and match any conditions:

- "Buy when RSI below 30 and price below 100, sell when RSI above 70 or price above 150"

## Output

The backtester generates a comprehensive visualization showing:

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

**Automatic Chart Opening:**

- Charts automatically open in your default image viewer
- High-resolution PNG (300 DPI) for clear analysis

## Strategy Parameters

### Default Settings

- **Initial Capital**: $10,000
- **Data Period**: 5 years of historical data
- **Position Size**: Maximum shares affordable with available cash

### Custom Initial Capital

Include your starting capital in the strategy:

```bash
python3 strategy_backtester.py AAPL "Buy when it dips 10 percent with $50000 initial capital"
```

## How It Works

1. **Parse Strategy**: Converts your natural language description into executable rules
2. **Fetch Data**: Downloads historical stock data (5 years)
3. **Run Simulation**: Iterates through historical data, executing trades when conditions are met
4. **Calculate Performance**: Tracks portfolio value, returns, and trade statistics
5. **Generate Visualization**: Creates comprehensive charts showing results
6. **Auto-Open**: Automatically displays the chart for analysis

## Data Sources

The tool fetches data from multiple sources:

1. **pandas-datareader** (primary): Stooq historical data
2. **yfinance** (fallback): Yahoo Finance data

## Advanced Features

### Financial Theory Testing (Optional)

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

## Technical Details

- **Runtime**: Python 3.9+ with pandas, numpy, matplotlib
- **Data Analysis**: Statistical tests including autocorrelation, rolling averages, and momentum calculations
- **Visualization**: High-resolution PNG charts with multiple indicators
- **Strategy Parsing**: Natural language processing for flexible strategy definitions

## Tips for Better Strategies

1. **Be Specific**: Use clear percentages or price targets
2. **Test Multiple Timeframes**: Try different dip/rise percentages
3. **Consider Volatility**: Adjust strategies based on stock volatility
4. **Combine Indicators**: Mix price-based with technical indicators
5. **Backtest Thoroughly**: Test on multiple stocks and time periods

## Example Results

**Strategy**: "Buy when it dips 10 percent, sell when it rises 10 percent"
**Stock**: AAPL
**Result**: +152.46% return over 5 years (18 trades)

**Strategy**: "Buy below 100, sell above 150"
**Stock**: NVDA
**Result**: +1086.73% return over 5 years (2 trades)

**Strategy**: "Buy when RSI below 30, sell when RSI above 70"
**Stock**: TSLA
**Result**: +157.34% return over 5 years (35 trades)

## Notes

- Strategies are backtested on historical data - past performance doesn't guarantee future results
- Some strategies may not trigger if conditions are never met
- Charts are saved as PNG files in the current directory
- The tool uses maximum position sizing (buys as many shares as possible with available cash)
- Transaction costs and slippage are not included in simulations
