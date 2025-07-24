import random
import numpy as np
from deap import base, creator, tools, algorithms
from functools import partial
import yaml
import os
import sys # Import sys for stdout redirection
from src.backtesting.engine import BacktestingEngine
from src.reporting.performance import PerformanceCalculator
from src.strategies.moving_average_crossover import MovingAverageCrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.mean_reversion import MeanReversion
from src.strategies.lstm_strategy import LSTMStrategy
from src.strategies.pairs_trading_strategy import PairsTradingStrategy
from src.data.data_loader import DataLoader

# --- Configuration --- #
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "config.yml")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Map strategy names to classes
STRATEGY_MAPPING = {
    "moving_average_crossover": MovingAverageCrossover,
    "rsi_strategy": RSIStrategy,
    "mean_reversion": MeanReversion,
    "lstm_strategy": LSTMStrategy,
    "pairs_trading_strategy": PairsTradingStrategy
}

# --- Genetic Algorithm Setup --- #
creator.create("FitnessMax", base.Fitness, weights=(1.0,)) # Maximize Sharpe Ratio
creator.create("Individual", list, fitness=creator.FitnessMax)

def clamp_individual_param(param_value, param_index, strategy_name):
    if strategy_name == "moving_average_crossover":
        if param_index == 0: return max(10, min(100, int(param_value)))
        if param_index == 1: return max(100, min(300, int(param_value)))
        if param_index == 2: return max(0.01, min(0.05, param_value))
    elif strategy_name == "rsi_strategy":
        if param_index == 0: return max(7, min(21, int(param_value)))
        if param_index == 1: return max(60.0, min(80.0, param_value))
        if param_index == 2: return max(20.0, min(40.0, param_value))
        if param_index == 3: return max(0.01, min(0.05, param_value))
    elif strategy_name == "mean_reversion":
        if param_index == 0: return max(10, min(50, int(param_value)))
        if param_index == 1: return max(1.0, min(3.0, param_value))
        if param_index == 2: return max(0.01, min(0.05, param_value))
    elif strategy_name == "lstm_strategy":
        if param_index == 0: return max(30, min(90, int(param_value)))
        if param_index == 1: return max(5, min(20, int(param_value)))
        if param_index == 2: return random.choice([16, 32, 64]) # Batch size is discrete
        if param_index == 3: return max(0.7, min(0.9, param_value))
        if param_index == 4: return max(0.01, min(0.05, param_value))
    elif strategy_name == "pairs_trading_strategy":
        if param_index == 0: return max(30, min(90, int(param_value)))
        if param_index == 1: return max(1.5, min(3.0, param_value))
        if param_index == 2: return max(0.0, min(1.0, param_value))
        if param_index == 3: return max(0.01, min(0.05, param_value))
    return param_value


    toolbox = setup_toolbox(strategy_name)
    toolbox = setup_toolbox(strategy_name)

    # Load data once
    data_loader = DataLoader(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))

    # Determine symbols to load based on strategy type
    symbols_to_load = []
    if strategy_name == "pairs_trading_strategy":
        # For pairs trading, get symbols from config
        pairs_config_found = False
        for item in CONFIG.get('strategies', []):
            if "pairs_trading_strategy" in item:
                symbols_to_load = item["pairs_trading_strategy"].get("symbols", [])
                pairs_config_found = True
                break
        if not pairs_config_found or not symbols_to_load:
            print(f"Error: Pairs trading strategy config or symbols not found for {strategy_name}. Skipping optimization.")
            return None, None
    else:
        # For single-asset strategies, load data for all tickers defined in config
        symbols_to_load = CONFIG['backtest'].get('tickers', [])
        if not symbols_to_load:
            print(f"Error: No tickers defined in backtest config for {strategy_name}. Skipping optimization.")
            return None, None

    data = data_loader.load_multiple_csvs(symbols_to_load)

    if data is None or data.empty:
        print(f"Error: Could not load data for {symbols_to_load}. Skipping optimization.")
        return None, None

    # Register the evaluate function with the loaded data and symbols
    toolbox.register("evaluate", evaluate_strategy_individual, strategy_name=strategy_name, symbols_to_load=symbols_to_load, data=data)

    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    if output_file:
        original_stdout = sys.stdout
        sys.stdout = open(output_file, 'w')

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=NGEN, stats=stats, halloffame=hof, verbose=True)

    if output_file:
        sys.stdout.close()
        sys.stdout = original_stdout

    return hof[0], stats

if __name__ == "__main__":
    # Example: Optimize MovingAverageCrossover
    best_individual, stats = run_optimization("moving_average_crossover", output_file="optimization_results_m_a_crossover.txt")
    if best_individual:
        print(f"Best MovingAverageCrossover Parameters: {best_individual}")
        print(f"Best MovingAverageCrossover Sharpe Ratio: {best_individual.fitness.values[0]}")

    # Example: Optimize RSIStrategy
    best_individual, stats = run_optimization("rsi_strategy", output_file="optimization_results_rsi.txt")
    if best_individual:
        print(f"Best RSIStrategy Parameters: {best_individual}")
        print(f"Best RSIStrategy Sharpe Ratio: {best_individual.fitness.values[0]}")

    # Example: Optimize MeanReversion
    best_individual, stats = run_optimization("mean_reversion", output_file="optimization_results_mean_reversion.txt")
    if best_individual:
        print(f"Best MeanReversion Parameters: {best_individual}")
        print(f"Best MeanReversion Sharpe Ratio: {best_individual.fitness.values[0]}")

    # Example: Optimize LSTMStrategy (Note: LSTM training is slow, reduce NGEN/POP_SIZE for quick tests)
    best_individual, stats = run_optimization("lstm_strategy", NGEN=10, POP_SIZE=10, output_file="optimization_results_lstm.txt")
    if best_individual:
        print(f"Best LSTMStrategy Parameters: {best_individual}")
        print(f"Best LSTMStrategy Sharpe Ratio: {best_individual.fitness.values[0]}")

    # Example: Optimize PairsTradingStrategy (Note: Requires specific symbols in config)
    best_individual, stats = run_optimization("pairs_trading_strategy", NGEN=10, POP_SIZE=10, output_file="optimization_results_pairs_trading.txt")
    if best_individual:
        print(f"Best PairsTradingStrategy Parameters: {best_individual}")
        print(f"Best PairsTradingStrategy Sharpe Ratio: {best_individual.fitness.values[0]}")
