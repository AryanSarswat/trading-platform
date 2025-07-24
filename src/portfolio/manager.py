from typing import Dict, List, Any

class PortfolioManager:
    """
    Manages the simulated trading portfolio, tracking cash, positions, and equity.
    """
    def __init__(self, initial_cash: float):
        """
        Initializes the PortfolioManager.

        Args:
            initial_cash: The initial amount of cash in the portfolio.
        """
        self.initial_cash: float = initial_cash
        self.cash: float = initial_cash
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.equity_curve: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []
        self.closed_trades: List[Dict[str, Any]] = []

    def update_portfolio(self, current_price: Dict[str, float], timestamp: Any):
        """
        Updates the portfolio's equity curve based on current market prices.

        Args:
            current_price: A dictionary mapping symbols to their current prices.
            timestamp: The current timestamp of the market data.
        """
        current_equity: float = self.cash
        for symbol, position in self.positions.items():
            current_equity += position['quantity'] * current_price.get(symbol, 0)
        self.equity_curve.append({'timestamp': timestamp, 'equity': current_equity})

    def execute_trade(self, trade: Dict[str, Any]) -> bool:
        """
        Executes a trade and updates cash and positions, handling both long and short positions.

        Args:
            trade: A dictionary containing trade details, including 'symbol', 'type' (buy/sell),
                   'quantity', 'price', and 'commission'.

        Returns:
            True if the trade was successful, False otherwise.
        """
        symbol: str = trade['symbol']
        trade_type: str = trade['type']
        quantity: float = trade['quantity']
        price: float = trade['price']
        commission: float = trade.get('commission', 0.0)

        # Ensure the symbol exists in positions, initialize if not
        if symbol not in self.positions:
            self.positions[symbol] = {'quantity': 0.0, 'avg_price': 0.0}

        current_quantity: float = self.positions[symbol]['quantity']
        current_avg_price: float = self.positions[symbol]['avg_price']

        if trade_type == 'buy':
            cost: float = quantity * price + commission
            if self.cash < cost:
                print(f"Insufficient cash to buy {quantity} of {symbol}")
                return False

            self.cash -= cost

            if current_quantity >= 0:  # Existing long position or no position
                new_total_value = (current_quantity * current_avg_price) + (quantity * price)
                new_total_quantity = current_quantity + quantity
                self.positions[symbol]['quantity'] = new_total_quantity
                self.positions[symbol]['avg_price'] = new_total_value / new_total_quantity if new_total_quantity > 0 else 0.0
            else:  # Existing short position (current_quantity < 0)
                # Buying to cover short
                if abs(current_quantity) <= quantity:  # Fully or over-covered short, potentially flipping to long
                    covered_quantity = abs(current_quantity)
                    pnl_from_cover = (current_avg_price - price) * covered_quantity
                    self.cash += pnl_from_cover  # Realize PnL from covering short

                    remaining_buy_quantity = quantity - covered_quantity
                    self.positions[symbol]['quantity'] = remaining_buy_quantity
                    self.positions[symbol]['avg_price'] = price  # New average for the new long position
                else:  # Partially covered short, still short
                    self.positions[symbol]['quantity'] += quantity
                    # avg_price for short remains the same as it's the average short entry price

        elif trade_type == 'sell':
            # Selling can reduce long or create/increase short
            if current_quantity > 0:  # Existing long position
                if current_quantity <= quantity:  # Selling to close long or go short
                    pnl_from_long_close = (price - current_avg_price) * current_quantity
                    self.cash += pnl_from_long_close - commission  # Realize PnL from closing long

                    remaining_sell_quantity = quantity - current_quantity
                    self.positions[symbol]['quantity'] = - (quantity - current_quantity) # Remaining quantity is short
                    if self.positions[symbol]['quantity'] == 0:
                        self.closed_trades.append({'symbol': symbol, 'pnl': pnl_from_long_close, 'timestamp': trade['timestamp']})
                        del self.positions[symbol]
                    else: # Flipped to short
                        self.positions[symbol]['avg_price'] = price  # New average for the new short position
                else:  # Reduce long position
                    self.cash += quantity * price - commission
                    new_total_value = (current_quantity * current_avg_price) - (quantity * price)
                    new_total_quantity = current_quantity - quantity
                    self.positions[symbol]['quantity'] = new_total_quantity
                    self.positions[symbol]['avg_price'] = new_total_value / new_total_quantity if new_total_quantity > 0 else 0.0

            else:  # No position or existing short position (current_quantity <= 0)
                # Create or increase short position
                self.cash += quantity * price - commission
                new_total_value = (abs(current_quantity) * current_avg_price) + (quantity * price)
                new_total_quantity = abs(current_quantity) + quantity
                self.positions[symbol]['quantity'] = -new_total_quantity
                self.positions[symbol]['avg_price'] = new_total_value / new_total_quantity if new_total_quantity > 0 else 0.0
        
        # If quantity becomes zero, remove the position
        if symbol in self.positions and self.positions[symbol]['quantity'] == 0:
            del self.positions[symbol]

        self.trades.append(trade)
        return True


