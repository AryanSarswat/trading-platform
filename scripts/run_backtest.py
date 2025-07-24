import os
import pandas as pd
import yaml
from typing import List, Dict, Any
from src.backtesting.engine import BacktestingEngine
from src.reporting.performance import PerformanceCalculator
from src.strategies.moving_average_crossover import MovingAverageCrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.mean_reversion import MeanReversion
from src.strategies.lstm_strategy import LSTMStrategy
from src.strategies.pairs_trading_strategy import PairsTradingStrategy
import json

def run_backtest_for_strategy(strategy_class, strategy_params, symbols: List[str], initial_cash, data_path):
    strategy_name = strategy_class.__name__
    print(f"\n--- Running Backtest for {strategy_name} on {symbols} ---")
    engine = BacktestingEngine(initial_cash=initial_cash, data_path=data_path)
    data = engine.load_data(symbols)

    if data is None or data.empty:
        print(f"Could not load data for {symbols}. Skipping backtest.\n")
        return None, None, None

    # Pass symbols to strategy based on its type
    if strategy_name == "PairsTradingStrategy":
        # Extract symbol1 and symbol2 from the symbols list
        # and pass other strategy_params directly
        strategy_specific_params = {k: v for k, v in strategy_params.items() if k != "symbols"}
        strategy = strategy_class(symbol1=symbols[0], symbol2=symbols[1], **strategy_specific_params)
    else:
        strategy = strategy_class(symbol=symbols[0], **strategy_params)
    
    engine.set_strategy(strategy)

    equity_curve, trades = engine.run_backtest()

    if equity_curve and trades:
        performance_calculator = PerformanceCalculator(equity_curve, trades, engine.portfolio_manager.closed_trades)
        performance_report = performance_calculator.generate_performance_report()
        print(f"Performance Report for {strategy_name} on {symbols}:")
        for metric, value in performance_report.items():
            print(f"  {metric}: {value:.4f}")
        return equity_curve, trades, performance_report
    else:
        print(f"No equity curve or trades generated for {strategy_name} on {symbols}.\n")
        return None, None, None

if __name__ == "__main__":
    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "config.yml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get backtest parameters
    initial_cash = config['backtest']['initial_cash']
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    # Map strategy names to classes
    strategy_mapping = {
        "moving_average_crossover": MovingAverageCrossover,
        "rsi_strategy": RSIStrategy,
        "mean_reversion": MeanReversion,
        "lstm_strategy": LSTMStrategy,
        "pairs_trading_strategy": PairsTradingStrategy
    }

    all_results = {}
    performance_summaries = {}

    for strategy_config in config['strategies']:
        strategy_name = list(strategy_config.keys())[0]
        strategy_params = strategy_config[strategy_name]
        strategy_class = strategy_mapping[strategy_name]

        if strategy_name == "pairs_trading_strategy":
            symbols_list = [strategy_params["symbols"]] # For pairs, symbols is already a list like ["AAPL", "MSFT"]
        else:
            symbols_list = [[s] for s in config['backtest']['tickers']] # For single asset, create list of lists like [["AAPL"], ["MSFT"]]

        for symbols in symbols_list:
            report_key_symbols = "-".join(symbols) if len(symbols) > 1 else symbols[0]

            if report_key_symbols not in all_results:
                all_results[report_key_symbols] = {}
                performance_summaries[report_key_symbols] = {}

            equity_curve_list, trades, performance_report = run_backtest_for_strategy(
                strategy_class, strategy_params, symbols, initial_cash, data_path
            )
            if equity_curve_list is not None and performance_report is not None:
                equity_curve_df = pd.DataFrame(equity_curve_list).set_index("timestamp")
                all_results[report_key_symbols][strategy_name] = {
                    "equity_curve": equity_curve_df.to_json(orient='split'),
                    "performance_report": performance_report
                }
                performance_summaries[report_key_symbols][strategy_name] = performance_report

    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "backtest_results.json")
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4)
    print(f"\n--- All Backtests Completed. Results saved to {output_file} ---")

    performance_summary_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "performance_summary.json")
    with open(performance_summary_file, "w") as f:
        json.dump(performance_summaries, f, indent=4)
    print(f"Performance summaries saved to {performance_summary_file}")


