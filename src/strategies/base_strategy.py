import pandas as pd
from typing import Any, Dict, Optional

class Strategy:
    """
    Base class for all trading strategies.
    """
    def __init__(self, symbol: str, stop_loss_percentage: float = 0.0):
        """
        Initializes the base strategy.

        Args:
            symbol: The trading symbol (e.g., 'AAPL').
            stop_loss_percentage: The percentage below the entry price at which to trigger a stop-loss.
        """
        self.symbol: str = symbol
        self.portfolio_manager: Optional[Any] = None
        self.data: Optional[pd.DataFrame] = None
        self.current_index: int = -1
        self.stop_loss_percentage: float = stop_loss_percentage
        self.entry_price: float = 0.0
        self.position_quantity: float = 0.0

    def initialize(self, portfolio_manager: Any):
        """
        Initializes the strategy with a portfolio manager.

        Args:
            portfolio_manager: An instance of the PortfolioManager.
        """
        self.portfolio_manager = portfolio_manager

    def set_data(self, data: pd.DataFrame):
        """
        Sets the historical data for the strategy.

        Args:
            data: A pandas DataFrame containing historical market data.
        """
        self.data = data

    def on_bar(self, index: int, row: pd.Series):
        """
        This method is called for each bar (time period) of data.
        Subclasses should implement their trading logic here.

        Args:
            index: The integer index of the current row in the full data.
            row: A pandas Series representing the current bar's data.
        """
        self.current_index = index
        raise NotImplementedError("on_bar method must be implemented by subclasses")

    def buy(self, quantity: float, price: float, commission: float = 0.0):
        """
        Executes a buy order.

        Args:
            quantity: The quantity to buy.
            price: The price at which to buy.
            commission: The commission for the trade (default is 0).
        """
        if self.data is None or self.portfolio_manager is None:
            raise RuntimeError("Data or PortfolioManager not set for strategy.")

        trade: Dict[str, Any] = {
            'symbol': self.symbol,
            'type': 'buy',
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'timestamp': self.data.index[self.current_index]
        }
        if self.portfolio_manager.execute_trade(trade):
            self.entry_price = price
            self.position_quantity = quantity

    def sell(self, quantity: float, price: float, commission: float = 0.0):
        """
        Executes a sell order.

        Args:
            quantity: The quantity to sell.
            price: The price at which to sell.
            commission: The commission for the trade (default is 0).
        """
        if self.data is None or self.portfolio_manager is None:
            raise RuntimeError("Data or PortfolioManager not set for strategy.")

        trade: Dict[str, Any] = {
            'symbol': self.symbol,
            'type': 'sell',
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'timestamp': self.data.index[self.current_index]
        }
        if self.portfolio_manager.execute_trade(trade):
            self.entry_price = 0.0
            self.position_quantity = 0.0

    def check_stop_loss(self, current_price: float):
        """
        Checks if a stop-loss condition is met and executes a sell order if it is.
        This method assumes a long position.

        Args:
            current_price: The current market price of the asset.
        """
        if self.position_quantity > 0 and self.stop_loss_percentage > 0:
            stop_loss_price = self.entry_price * (1 - self.stop_loss_percentage)
            if current_price <= stop_loss_price:
                self.sell(self.position_quantity, current_price)
                print(f"STOP LOSS triggered for {self.symbol} at {current_price:.2f}")


