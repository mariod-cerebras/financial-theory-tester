# Financial Theory Tester

Test financial theories on stocks of your choice using historical data analysis and visualization.

## Features

- **Efficient Market Hypothesis Test**: Checks if stock follows random walk patterns
- **Momentum Theory Test**: Analyzes if past winners continue to outperform
- **Mean Reversion Test**: Determines if stock prices revert to their mean
- **Value Investing Test**: Evaluates if stock appears undervalued based on P/E ratios
- **Technical Analysis Test**: Provides insights using moving averages and RSI
- **Visual Analysis**: Generate comprehensive graphs showing buy/sell signals and theory explanations

## Installation

Install Python dependencies:

```bash
python3 -m pip install pandas numpy pandas-datareader yfinance matplotlib
```

Install Bun dependencies:

```bash
bun install
```

## Usage

### Text Analysis (Recommended for quick results)

```bash
python3 financial_theory_tester.py <TICKER> [period]
```

### Visual Analysis (Recommended for understanding)

```bash
python3 financial_theory_visualizer.py <TICKER> [period]
```

### Using Bun wrapper

```bash
bun run index.ts <TICKER> [period]
```

### Examples

Test Apple stock with visualizations:

```bash
python3 financial_theory_visualizer.py AAPL 2y
```

Test NVIDIA stock over 1 year:

```bash
python3 financial_theory_visualizer.py NVDA 1y
```

Test Tesla stock year-to-date:

```bash
python3 financial_theory_visualizer.py TSLA ytd
```

### Period Options

- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years (default)
- `5y` - 5 years
- `10y` - 10 years
- `ytd` - Year to date

## Output

### Text Analysis Output

The tool provides:

1. **Theory Test Results**: Each financial theory is tested with specific metrics
2. **Interpretation**: Plain language explanation of what the results mean
3. **Makes Sense**: Whether the theory appears to apply to this stock
4. **Summary**: Overall count of theories that make sense for the stock

### Visual Analysis Output

The visualizer generates 4 comprehensive PNG files:

1. **`{TICKER}_price_signals.png`**: Price chart with buy/sell signals
   - Stock price with 50-day and 200-day moving averages
   - Green triangles (▲) = BUY signals
   - Red triangles (▼) = SELL signals
   - RSI indicator showing overbought/oversold conditions

2. **`{TICKER}_momentum.png`**: Momentum analysis
   - 3-month and 12-month momentum trends
   - Daily returns distribution
   - Correlation analysis between past and future returns

3. **`{TICKER}_mean_reversion.png`**: Mean reversion analysis
   - Price with 20-day mean and ±2 standard deviation bands
   - Z-score chart showing price deviations
   - Extreme high/low points highlighted

4. **`{TICKER}_theory_summary.png`**: Comprehensive theory summary
   - All 4 theories tested with visual indicators
   - Color-coded results (green = makes sense, red = doesn't make sense)
   - Technical analysis indicators summary
   - Signal count and performance summary

### Example Output

```
============================================================
FINANCIAL THEORY TEST RESULTS: AAPL
============================================================

Fetching data for AAPL...
✓ Fetched 502 days of data using pandas-datareader

📊 Efficient Market Hypothesis
   Interpretation: Stock follows random walk
   Makes Sense: ✓ Yes

📊 Momentum Theory
   Interpretation: Stock shows momentum patterns
   Makes Sense: ✓ Yes

📊 Mean Reversion
   Interpretation: No clear mean reversion
   Makes Sense: ✗ No

📊 Technical Analysis
   Interpretation: Oversold - potential buy signal
   Makes Sense: ✗ No

============================================================
SUMMARY: 2/4 theories make sense for AAPL
============================================================
```

## Buy/Sell Signals

The visualizer generates buy/sell signals based on multiple theories:

**BUY Signals (Green ▲):**

- Golden Cross (50-day MA crosses above 200-day MA)
- RSI Oversold (< 30)
- Mean Reversion (price > 2 standard deviations below mean)

**SELL Signals (Red ▼):**

- Death Cross (50-day MA crosses below 200-day MA)
- RSI Overbought (> 70)
- Mean Reversion (price > 2 standard deviations above mean)

## Data Sources

The tool attempts to fetch data from multiple sources:

1. **pandas-datareader** (primary): Stooq historical data (most reliable)
2. **yfinance** (fallback): Yahoo Finance data

**Note**: Due to Python 3.9 compatibility issues with some yfinance versions, the tool prioritizes pandas-datareader which provides reliable historical stock data.

## Technical Details

- **Runtime**: Python 3.9+ with pandas, numpy, matplotlib
- **CLI Wrapper**: Bun/TypeScript for easy execution
- **Data Analysis**: Statistical tests including autocorrelation, rolling averages, and momentum calculations
- **Visualization**: High-resolution PNG charts with multiple indicators

## Notes

- Some tests require minimum data periods (e.g., momentum test needs 12+ months)
- Value investing test requires stock info (P/E ratio) which may not be available for all stocks
- Technical analysis uses 50-day and 200-day moving averages plus 14-day RSI
- Visualizations are saved as PNG files in the current directory
- Graphs include color-coded indicators showing which theories "make sense" (green) vs "don't make sense" (red)
