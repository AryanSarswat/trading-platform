import pandas as pd
from src.data.data_loader import DataLoader
from src.portfolio.manager import PortfolioManager
import logging
from typing import Optional, Tuple, List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BacktestingEngine:
    """
    Core backtesting engine that simulates trades and manages the backtesting process.
    """
    def __init__(self, initial_cash: float, data_path: str):
        """
        Initializes the BacktestingEngine.

        Args:
            initial_cash: The initial cash for the portfolio.
            data_path: The path to the data directory.
        """
        self.portfolio_manager: PortfolioManager = PortfolioManager(initial_cash)
        self.data_loader: DataLoader = DataLoader(data_path)
        self.strategy: Optional[Any] = None  # Type hint for strategy object
        self.data: Optional[pd.DataFrame] = None

    def load_data(self, symbols: List[str]) -> Optional[pd.DataFrame]:
        """
        Loads historical data for backtesting.

        Args:
            symbols: A list of ticker symbols (e.g., ["AAPL", "MSFT"]).

        Returns:
            A pandas DataFrame containing the loaded data, or None if loading fails.
        """
        self.data = self.data_loader.load_multiple_csvs(symbols)
        if self.data is not None:
            logging.info(f"Data loaded successfully for {symbols}")
        return self.data

    def set_strategy(self, strategy: Any):
        """
        Sets the trading strategy to be used for backtesting.

        Args:
            strategy: An instance of a trading strategy class.
        """
        self.strategy = strategy
        logging.info(f"Strategy {strategy.__class__.__name__} set.")

    def run_backtest(self) -> Optional[Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
        """
        Runs the backtest simulation.

        Iterates through the historical data, updates the portfolio, and executes
        trades based on the defined strategy.

        Returns:
            A tuple containing the equity curve (list of dicts) and trades (list of dicts),
            or None if data or strategy is not set.
        """
        if self.data is None:
            logging.error("No data loaded. Please load data before running backtest.")
            return None
        if self.strategy is None:
            logging.error("No strategy set. Please set a strategy before running backtest.")
            return None

        logging.info("Starting backtest...")
        self.strategy.initialize(self.portfolio_manager)

        # Pass the entire data to the strategy, and let the strategy handle slicing
        self.strategy.set_data(self.data)

        for i, (index, row) in enumerate(self.data.iterrows()):
            current_prices = {}
            for col in self.data.columns:
                if col.startswith("Close_"):
                    symbol = col.replace("Close_", "")
                    current_prices[symbol] = row[col]

            self.portfolio_manager.update_portfolio(current_prices, index)
            # Check for stop-loss before executing strategy's on_bar logic
            # This assumes the strategy is managing a single primary symbol for stop-loss
            if hasattr(self.strategy, 'symbol') and self.strategy.symbol in current_prices:
                self.strategy.check_stop_loss(current_prices[self.strategy.symbol])
            self.strategy.on_bar(i, row) # Pass index 'i' and the full row of data

        logging.info("Backtest finished.")
        return self.portfolio_manager.equity_curve, self.portfolio_manager.trades


