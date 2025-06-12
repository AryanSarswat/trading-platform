from .base_strategy import Strategy
import pandas as pd
import numpy as np

class MeanReversion(Strategy):
    """
    A trading strategy based on the principle of mean reversion.
    Assumes that prices will revert to their historical average.
    Buys when price is significantly below a moving average.
    Sells when price is significantly above a moving average.
    """
    def __init__(self, symbol, window=20, num_std_dev=2):
        super().__init__(symbol)
        self.window = window
        self.num_std_dev = num_std_dev
        self.in_position = False

    def on_bar(self, index, row):
        self.current_index = index # Store current index for buy/sell methods

        if index < self.window - 1:
            return

        historical_data = self.data.iloc[:index+1]

        rolling_mean = historical_data["Close"].rolling(window=self.window).mean().iloc[-1]
        rolling_std = historical_data["Close"].rolling(window=self.window).std().iloc[-1]

        upper_band = rolling_mean + (rolling_std * self.num_std_dev)
        lower_band = rolling_mean - (rolling_std * self.num_std_dev)

        current_price = row["Close"]

        if current_price < lower_band and not self.in_position:
            # Buy signal
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif current_price > upper_band and self.in_position:
            # Sell signal
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


