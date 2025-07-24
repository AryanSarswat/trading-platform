from src.strategies.base_strategy import Strategy
import pandas as pd
import numpy as np
from collections import deque
import logging

class PairsTradingStrategy(Strategy):
    """
    A pairs trading strategy that trades on the mean-reversion of a spread
    between two correlated assets.
    """
    def __init__(self, symbol1: str, symbol2: str, window: int = 60, entry_zscore: float = 2.0, exit_zscore: float = 0.5, stop_loss_percentage: float = 0.0):
        # For pairs trading, the 'symbol' in the base strategy is less relevant.
        # We'll use symbol1 as the primary symbol for portfolio management tracking.
        super().__init__(symbol1, stop_loss_percentage=stop_loss_percentage)
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.window = window
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore
        self.in_position = False
        self.prices1_history = deque(maxlen=window)
        self.prices2_history = deque(maxlen=window)
        self.current_spread = None
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def set_data(self, data: pd.DataFrame):
        # For pairs trading, data will contain both symbols. We need to adjust.
        # This strategy assumes 'data' is a multi-indexed DataFrame or has columns like 'symbol1_Close', 'symbol2_Close'
        # For simplicity, let's assume data has columns 'Close_SYMBOL1' and 'Close_SYMBOL2'
        self.data = data

    def on_bar(self, index: int, row: pd.Series):
        self.current_index = index

        if self.data is None:
            raise RuntimeError("Data not set for strategy.")

        # Assuming data has columns like 'Close_AAPL', 'Close_MSFT'
        try:
            price1 = row[f"Close_{self.symbol1}"]
            price2 = row[f"Close_{self.symbol2}"]
        except KeyError:
            logging.error(f"Missing price data for {self.symbol1} or {self.symbol2} in row. Skipping.")
            return

        self.prices1_history.append(price1)
        self.prices2_history.append(price2)

        if len(self.prices1_history) < self.window:
            return

        # Calculate spread (simple difference for now, can be ratio or cointegrated residual)
        spread_series = pd.Series(np.array(self.prices1_history) - np.array(self.prices2_history))
        
        mean_spread = spread_series.mean()
        std_spread = spread_series.std()

        if std_spread == 0:
            return # Avoid division by zero

        self.current_spread = price1 - price2
        zscore = (self.current_spread - mean_spread) / std_spread

        # Trading logic
        if not self.in_position:
            if zscore > self.entry_zscore: # Spread is too wide, short symbol1, long symbol2
                # Short symbol1, Long symbol2
                # For simplicity, let's assume equal dollar amounts for now
                quantity1 = int(self.portfolio_manager.cash * 0.5 / price1)
                quantity2 = int(self.portfolio_manager.cash * 0.5 / price2)
                if quantity1 > 0 and quantity2 > 0:
                    self.sell(quantity1, price1) # Short symbol1
                    self.buy(quantity2, price2) # Long symbol2
                    self.in_position = True
                    logging.info(f"{row.name}: ENTER PAIR (Short {self.symbol1}, Long {self.symbol2}) at Spread: {self.current_spread:.2f}, Z-score: {zscore:.2f}")
            elif zscore < -self.entry_zscore: # Spread is too narrow, long symbol1, short symbol2
                # Long symbol1, Short symbol2
                quantity1 = int(self.portfolio_manager.cash * 0.5 / price1)
                quantity2 = int(self.portfolio_manager.cash * 0.5 / price2)
                if quantity1 > 0 and quantity2 > 0:
                    self.buy(quantity1, price1) # Long symbol1
                    self.sell(quantity2, price2) # Short symbol2
                    self.in_position = True
                    logging.info(f"{row.name}: ENTER PAIR (Long {self.symbol1}, Short {self.symbol2}) at Spread: {self.current_spread:.2f}, Z-score: {zscore:.2f}")
        else: # In a position, look for exit
            if abs(zscore) < self.exit_zscore:
                # Close position
                # Check current positions and close them
                if self.portfolio_manager is None:
                    raise RuntimeError("PortfolioManager not set for strategy.")

                # Get current quantities for both symbols
                qty1 = self.portfolio_manager.positions.get(self.symbol1, {}).get("quantity", 0)
                qty2 = self.portfolio_manager.positions.get(self.symbol2, {}).get("quantity", 0)

                # Close position for symbol1 if open
                if qty1 != 0:
                    if qty1 > 0: # Long position
                        self.sell(qty1, price1)
                    else: # Short position
                        self.buy(abs(qty1), price1)

                # Close position for symbol2 if open
                if qty2 != 0:
                    if qty2 > 0: # Long position
                        self.sell(qty2, price2)
                    else: # Short position
                        self.buy(abs(qty2), price2)

                self.in_position = False
                logging.info(f"{row.name}: EXIT PAIR at Spread: {self.current_spread:.2f}, Z-score: {zscore:.2f}")
