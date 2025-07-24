from src.strategies.base_strategy import Strategy
import pandas as pd
from collections import deque
from typing import Any

class MovingAverageCrossover(Strategy):
    """
    A trading strategy based on the crossover of two moving averages.
    Buys when the short moving average crosses above the long moving average.
    Sells when the short moving average crosses below the long moving average.
    """
    def __init__(self, symbol: str, short_window: int = 50, long_window: int = 200, stop_loss_percentage: float = 0.0):
        """
        Initializes the MovingAverageCrossover strategy.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            short_window: The window size for the short moving average.
            long_window: The window size for the long moving average.
            stop_loss_percentage: The percentage below the entry price at which to trigger a stop-loss.
        """
        super().__init__(symbol, stop_loss_percentage=stop_loss_percentage)
        self.short_window: int = short_window
        self.long_window: int = long_window
        self.close_prices: deque = deque(maxlen=long_window)
        self.in_position: bool = False

    def on_bar(self, index: int, row: pd.Series):
        """
        Executes the moving average crossover trading logic for each bar.

        Args:
            index: The current index of the data.
            row: The current row of market data.
        """
        self.current_index = index
        current_price = row[f"Close_{self.symbol}"]
        self.close_prices.append(current_price)

        if self.data is None:
            raise RuntimeError("Data not set for strategy.")

        if len(self.close_prices) < self.long_window:
            return

        prices_series = pd.Series(list(self.close_prices))

        short_ma = prices_series.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = prices_series.rolling(window=self.long_window).mean().iloc[-1]

        if short_ma > long_ma and not self.in_position:
            # Buy signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif short_ma < long_ma and self.in_position:
            # Sell signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


