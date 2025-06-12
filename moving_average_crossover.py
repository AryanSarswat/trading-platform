from .base_strategy import Strategy
import pandas as pd
from collections import deque

class MovingAverageCrossover(Strategy):
    """
    A trading strategy based on the crossover of two moving averages.
    Buys when the short moving average crosses above the long moving average.
    Sells when the short moving average crosses below the long moving average.
    """
    def __init__(self, symbol, short_window=50, long_window=200):
        super().__init__(symbol)
        self.short_window = short_window
        self.long_window = long_window
        self.close_prices = deque(maxlen=long_window) # Use deque for efficient rolling window
        self.in_position = False

    def on_bar(self, index, row):
        self.current_index = index # Store current index for buy/sell methods
        self.close_prices.append(row["Close"])

        if len(self.close_prices) < self.long_window:
            return

        prices_series = pd.Series(list(self.close_prices))

        short_ma = prices_series.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = prices_series.rolling(window=self.long_window).mean().iloc[-1]

        current_price = row["Close"]

        if short_ma > long_ma and not self.in_position:
            # Buy signal
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif short_ma < long_ma and self.in_position:
            # Sell signal
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


