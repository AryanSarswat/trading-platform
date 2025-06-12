class PortfolioManager:
    """
    Manages the simulated trading portfolio, tracking cash, positions, and equity.
    """
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}
        self.equity_curve = []
        self.trades = []

    def update_portfolio(self, current_price, timestamp):
        """
        Updates the portfolio's equity curve based on current market prices.
        """
        current_equity = self.cash
        for symbol, position in self.positions.items():
            current_equity += position['quantity'] * current_price.get(symbol, 0)
        self.equity_curve.append({'timestamp': timestamp, 'equity': current_equity})

    def execute_trade(self, trade):
        """
        Executes a trade and updates cash and positions.
        Trade should be a dictionary with 'symbol', 'type' (buy/sell), 'quantity', 'price', 'commission'.
        """
        symbol = trade['symbol']
        trade_type = trade['type']
        quantity = trade['quantity']
        price = trade['price']
        commission = trade.get('commission', 0)

        if trade_type == 'buy':
            cost = quantity * price + commission
            if self.cash >= cost:
                self.cash -= cost
                self.positions[symbol] = self.positions.get(symbol, {'quantity': 0, 'avg_price': 0})
                current_total_cost = self.positions[symbol]['quantity'] * self.positions[symbol]['avg_price']
                new_total_cost = current_total_cost + quantity * price
                new_quantity = self.positions[symbol]['quantity'] + quantity
                self.positions[symbol]['quantity'] = new_quantity
                self.positions[symbol]['avg_price'] = new_total_cost / new_quantity if new_quantity > 0 else 0
                self.trades.append(trade)
                return True
            else:
                print(f"Insufficient cash to buy {quantity} of {symbol}")
                return False
        elif trade_type == 'sell':
            if symbol in self.positions and self.positions[symbol]['quantity'] >= quantity:
                self.cash += quantity * price - commission
                self.positions[symbol]['quantity'] -= quantity
                if self.positions[symbol]['quantity'] == 0:
                    del self.positions[symbol]
                self.trades.append(trade)
                return True
            else:
                print(f"Insufficient {symbol} to sell {quantity}")
                return False
        return False


