import pandas as pd
from .data_loader import DataLoader
from .portfolio_manager import PortfolioManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BacktestingEngine:
    """
    Core backtesting engine that simulates trades and manages the backtesting process.
    """
    def __init__(self, initial_cash, data_path):
        self.portfolio_manager = PortfolioManager(initial_cash)
        self.data_loader = DataLoader(data_path)
        self.strategy = None
        self.data = None

    def load_data(self, file_name):
        self.data = self.data_loader.load_csv(file_name)
        if self.data is not None:
            logging.info(f"Data loaded successfully for {file_name}")
        return self.data

    def set_strategy(self, strategy):
        self.strategy = strategy
        logging.info(f"Strategy {strategy.__class__.__name__} set.")

    def run_backtest(self):
        if self.data is None:
            logging.error("No data loaded. Please load data before running backtest.")
            return
        if self.strategy is None:
            logging.error("No strategy set. Please set a strategy before running backtest.")
            return

        logging.info("Starting backtest...")
        self.strategy.initialize(self.portfolio_manager)

        # Pass the entire data to the strategy, and let the strategy handle slicing
        self.strategy.set_data(self.data)

        for i, (index, row) in enumerate(self.data.iterrows()):
            current_prices = {self.strategy.symbol: row["Close"]}
            self.portfolio_manager.update_portfolio(current_prices, index)
            self.strategy.on_bar(i, row) # Pass index 'i' for current position in data

        logging.info("Backtest finished.")
        return self.portfolio_manager.equity_curve, self.portfolio_manager.trades


