from src.strategies.base_strategy import Strategy
import pandas as pd
from collections import deque
from typing import Any

class RSIStrategy(Strategy):
    """
    A trading strategy based on the Relative Strength Index (RSI).
    Buys when RSI crosses below a certain oversold threshold (e.g., 30).
    Sells when RSI crosses above a certain overbought threshold (e.g., 70).
    """
    def __init__(self, symbol: str, rsi_period: int = 14, overbought_threshold: float = 70.0, oversold_threshold: float = 30.0, stop_loss_percentage: float = 0.0):
        """
        Initializes the RSIStrategy.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            rsi_period: The period for calculating the RSI.
            overbought_threshold: The RSI threshold for overbought conditions.
            oversold_threshold: The RSI threshold for oversold conditions.
            stop_loss_percentage: The percentage below the entry price at which to trigger a stop-loss.
        """
        super().__init__(symbol, stop_loss_percentage=stop_loss_percentage)
        self.rsi_period: int = rsi_period
        self.overbought_threshold: float = overbought_threshold
        self.oversold_threshold: float = oversold_threshold
        self.close_prices: deque = deque(maxlen=rsi_period)
        self.in_position: bool = False

    def calculate_rsi(self, prices: pd.Series, period: int) -> float:
        """
        Calculates the Relative Strength Index (RSI).

        Args:
            prices: A pandas Series of close prices.
            period: The period for RSI calculation.

        Returns:
            The calculated RSI value.
        """
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] # Return the last RSI value

    def on_bar(self, index: int, row: pd.Series):
        """
        Executes the RSI trading logic for each bar.

        Args:
            index: The current index of the data.
            row: The current row of market data.
        """
        self.current_index = index
        current_price = row[f"Close_{self.symbol}"]
        self.close_prices.append(current_price)

        if self.data is None:
            raise RuntimeError("Data not set for strategy.")

        if len(self.close_prices) < self.rsi_period:
            return

        prices_series = pd.Series(list(self.close_prices))
        rsi = self.calculate_rsi(prices_series, self.rsi_period)

        if rsi < self.oversold_threshold and not self.in_position:
            # Buy signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif rsi > self.overbought_threshold and self.in_position:
            # Sell signal
            if self.portfolio_manager is None:
                raise RuntimeError("PortfolioManager not set for strategy.")
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


