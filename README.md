# Quant Trading Algorithm Repository

This repository provides a robust and modular framework for developing, backtesting, and analyzing quantitative trading strategies. Built with a focus on clean code, performance, and extensibility, it aims to be a state-of-the-art platform for quantitative research.

## Features

- **Modular Design:** Separated components for data loading, strategy implementation, portfolio management, backtesting, and performance reporting.
- **Configurable Backtesting:** Easily configure backtests using a YAML configuration file.
- **Comprehensive Performance Metrics:** Detailed performance analysis including Sharpe Ratio, Sortino Ratio, Max Drawdown, CAGR, and Win/Loss Ratio.
-   **Moving Average Crossover:** A trend-following strategy based on the crossover of a short-term and long-term moving average.
-   **RSI Strategy:** A momentum strategy utilizing the Relative Strength Index to identify overbought and oversold conditions.
-   **Mean Reversion:** A strategy that assumes prices will revert to their historical average, buying when prices are low and selling when high.
-   **LSTM Strategy:** A strategy utilizing Long Short-Term Memory neural networks for price prediction and signal generation.
-   **Pairs Trading Strategy:** A mean-reversion strategy that exploits the temporary divergence of two historically correlated assets.
- **Data Management:** Tools for downloading historical market data.
- **Professional Codebase:** Adheres to PEP 8, includes type hints, and comprehensive docstrings.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/trading-algorithms.git
    cd trading-algorithms
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` will be generated in a later step.)*

## Usage

### 1. Download Historical Data

First, download the historical data for the assets you want to backtest. The `download_data.py` script uses `yfinance` to fetch data.

```bash
python scripts/download_data.py
```

This will download data for AAPL, MSFT, and GOOGL by default and save them in the `data/` directory.

### 2. Configure Backtest

Edit the `configs/config.yml` file to define your backtesting parameters, including initial cash, tickers, and strategy-specific parameters.

```yaml
# configs/config.yml
backtest:
  initial_cash: 100000
  tickers:
    - "AAPL"
    - "MSFT"
    - "GOOGL"

strategies:
  moving_average_crossover:
    short_window: 50
    long_window: 200
  rsi_strategy:
    rsi_period: 14
    overbought_threshold: 70
    oversold_threshold: 30
  mean_reversion:
    window: 20
    num_std_dev: 2
```

### 3. Run Backtest

Execute the `run_backtest.py` script to run the backtesting process based on your configuration.

```bash
python scripts/run_backtest.py
```

Results (equity curves and performance summaries) will be saved in the `reports/` directory.

### 4. Generate Performance Table

After running backtests, you can generate a markdown table summarizing the performance of all strategies across all tickers.

```bash
python scripts/generate_report.py
```

This will create `performance_summary_table.md` in the root directory.

### 5. Plot Equity Curves

To visualize the equity curves of your backtests:

```bash
python src/visualization/plotter.py
```

This will generate PNG images of equity curves in the `reports/` directory.

## Project Structure

```
.  
├── configs/                  # Configuration files (e.g., config.yml)
├── data/                     # Stores historical market data (downloaded by scripts/download_data.py)
├── docs/                     # Project documentation
├── reports/                  # Backtest results, performance summaries, and plots
├── scripts/                  # Standalone scripts for data download, running backtests, etc.
│   ├── download_data.py
│   ├── generate_report.py
│   └── run_backtest.py
├── src/                      # Core source code of the backtesting framework
│   ├── __init__.py
│   ├── backtesting/          # Backtesting engine and related logic
│   │   └── engine.py
│   ├── data/                 # Data loading and handling utilities
│   │   └── data_loader.py
│   ├── portfolio/            # Portfolio management logic
│   │   └── manager.py
│   ├── reporting/            # Performance calculation and reporting
│   │   └── performance.py
│   ├── strategies/           # Implementations of various trading strategies
│   │   ├── base_strategy.py
│   │   ├── mean_reversion.py
│   │   ├── moving_average_crossover.py
│   │   └── rsi_strategy.py
│   ├── utils/                # General utility functions
│   └── visualization/        # Plotting and dashboard components
│       └── plotter.py
├── tests/                    # Unit tests for the codebase
│   └── test_performance.py
├── .gitignore
├── backtesting_platform_architecture.md
├── performance_summary_table.md
└── README.md
```

## Strategies Implemented

-   **Moving Average Crossover:** A trend-following strategy based on the crossover of a short-term and long-term moving average.
-   **RSI Strategy:** A momentum strategy utilizing the Relative Strength Index to identify overbought and oversold conditions.
-   **Mean Reversion:** A strategy that assumes prices will revert to their historical average, buying when prices are low and selling when high.

## Performance Metrics

-   **Sharpe Ratio:** Measures risk-adjusted return.
-   **Sortino Ratio:** Similar to Sharpe, but only considers downside deviation.
-   **Max Drawdown:** The largest peak-to-trough decline in equity.
-   **Win/Loss Ratio:** The ratio of winning trades to losing trades.
-   **CAGR (Compound Annual Growth Rate):** The annualized rate of return of an investment over a specified period.
-   **Volatility:** The degree of variation of a trading price series over time.