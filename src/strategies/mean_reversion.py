from src.strategies.base_strategy import Strategy
import pandas as pd
import numpy as np
from typing import Any

class MeanReversion(Strategy):
    """
    A trading strategy based on the principle of mean reversion.
    Assumes that prices will revert to their historical average.
    Buys when price is significantly below a moving average.
    Sells when price is significantly above a moving average.
    """
    def __init__(self, symbol: str, window: int = 20, num_std_dev: float = 2.0, stop_loss_percentage: float = 0.0):
        """
        Initializes the MeanReversion strategy.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            window: The look-back window for calculating the moving average.
            num_std_dev: The number of standard deviations for the bands.
            stop_loss_percentage: The percentage below the entry price at which to trigger a stop-loss.
        """
        super().__init__(symbol, stop_loss_percentage=stop_loss_percentage)
        self.window: int = window
        self.num_std_dev: float = num_std_dev
        self.in_position: bool = False

    def on_bar(self, index: int, row: pd.Series):
        """
        Executes the mean reversion trading logic for each bar.

        Args:
            index: The current index of the data.
            row: The current row of market data.
        """
        self.current_index = index

        if self.data is None:
            raise RuntimeError("Data not set for strategy.")

        if index < self.window - 1:
            return

        historical_data = self.data.iloc[:index+1]

        rolling_mean = historical_data[f"Close_{self.symbol}"].rolling(window=self.window).mean().iloc[-1]
        rolling_std = historical_data[f"Close_{self.symbol}"].rolling(window=self.window).std().iloc[-1]

        upper_band = rolling_mean + (rolling_std * self.num_std_dev)
        lower_band = rolling_mean - (rolling_std * self.num_std_dev)

        current_price = row[f"Close_{self.symbol}"]

        if current_price < lower_band and not self.in_position:
            # Buy signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif current_price > upper_band and self.in_position:
            # Sell signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


