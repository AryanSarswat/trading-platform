from .base_strategy import Strategy
import pandas as pd
from collections import deque

class RSIStrategy(Strategy):
    """
    A trading strategy based on the Relative Strength Index (RSI).
    Buys when RSI crosses below a certain oversold threshold (e.g., 30).
    Sells when RSI crosses above a certain overbought threshold (e.g., 70).
    """
    def __init__(self, symbol, rsi_period=14, overbought_threshold=70, oversold_threshold=30):
        super().__init__(symbol)
        self.rsi_period = rsi_period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.close_prices = deque(maxlen=rsi_period) # Use deque for efficient rolling window
        self.in_position = False

    def calculate_rsi(self, prices, period):
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def on_bar(self, index, row):
        self.current_index = index # Store current index for buy/sell methods
        self.close_prices.append(row["Close"])

        if len(self.close_prices) < self.rsi_period:
            return

        prices_series = pd.Series(list(self.close_prices))
        rsi = self.calculate_rsi(prices_series, self.rsi_period).iloc[-1]

        current_price = row["Close"]

        if rsi < self.oversold_threshold and not self.in_position:
            # Buy signal
            quantity_to_buy = int(self.portfolio_manager.cash / current_price)
            if quantity_to_buy > 0:
                self.buy(quantity_to_buy, current_price)
                self.in_position = True
                print(f"{row.name}: BUY {quantity_to_buy} of {self.symbol} at {current_price}")
        elif rsi > self.overbought_threshold and self.in_position:
            # Sell signal
            quantity_to_sell = self.portfolio_manager.positions.get(self.symbol, {}).get("quantity", 0)
            if quantity_to_sell > 0:
                self.sell(quantity_to_sell, current_price)
                self.in_position = False
                print(f"{row.name}: SELL {quantity_to_sell} of {self.symbol} at {current_price}")


