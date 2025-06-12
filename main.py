import os
import pandas as pd
from core.backtesting_engine import BacktestingEngine
from metrics.performance_calculator import PerformanceCalculator
from strategies.moving_average_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.mean_reversion import MeanReversion
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
INITIAL_CASH = 100000

def run_single_backtest(strategy_class, ticker, initial_cash=INITIAL_CASH):
    print(f"\n--- Running Backtest for {strategy_class.__name__} on {ticker} ---")
    engine = BacktestingEngine(initial_cash=initial_cash, data_path=DATA_PATH)
    data_file = f"{ticker}.csv"
    data = engine.load_data(data_file)

    if data is None or data.empty:
        print(f"Could not load data for {ticker}. Skipping backtest.\n")
        return None, None, None

    strategy = strategy_class(symbol=ticker)
    engine.set_strategy(strategy)

    equity_curve, trades = engine.run_backtest()

    if equity_curve and trades:
        performance_calculator = PerformanceCalculator(equity_curve, trades)
        performance_report = performance_calculator.generate_performance_report()
        print(f"Performance Report for {strategy_class.__name__} on {ticker}:")
        for metric, value in performance_report.items():
            print(f"  {metric}: {value:.4f}")
        return equity_curve, trades, performance_report
    else:
        print(f"No equity curve or trades generated for {strategy_class.__name__} on {ticker}.\n")
        return None, None, None

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL"]
    strategies = [
        MovingAverageCrossover,
        RSIStrategy,
        MeanReversion
    ]

    all_results = {}
    performance_summaries = {}

    for ticker in tickers:
        all_results[ticker] = {}
        performance_summaries[ticker] = {}
        for strategy_class in strategies:
            equity_curve_list, trades, performance_report = run_single_backtest(strategy_class, ticker)
            if equity_curve_list is not None and performance_report is not None:
                # Convert equity_curve_list (which is a list of dicts) to a DataFrame
                equity_curve_df = pd.DataFrame(equity_curve_list).set_index("timestamp")
                all_results[ticker][strategy_class.__name__] = {
                    "equity_curve": equity_curve_df.to_json(orient='split'),
                    "performance_report": performance_report
                }
                performance_summaries[ticker][strategy_class.__name__] = performance_report

    output_file = os.path.join(os.path.dirname(__file__), "reports", "backtest_results.json")
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4)
    print(f"\n--- All Backtests Completed. Results saved to {output_file} ---")

    performance_summary_file = os.path.join(os.path.dirname(__file__), "reports", "performance_summary.json")
    with open(performance_summary_file, "w") as f:
        json.dump(performance_summaries, f, indent=4)
    print(f"Performance summaries saved to {performance_summary_file}")


