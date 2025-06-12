class Strategy:
    """
    Base class for all trading strategies.
    """
    def __init__(self, symbol):
        self.symbol = symbol
        self.portfolio_manager = None
        self.data = None # This will now hold the full historical data
        self.current_index = -1 # Initialize current_index

    def initialize(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager

    def set_data(self, data):
        self.data = data

    def on_bar(self, index, row):
        """
        This method is called for each bar (time period) of data.
        Subclasses should implement their trading logic here.
        `index` is the integer index of the current row in the full data.
        """
        self.current_index = index # Update current_index in on_bar
        raise NotImplementedError("on_bar method must be implemented by subclasses")

    def buy(self, quantity, price, commission=0):
        trade = {
            'symbol': self.symbol,
            'type': 'buy',
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'timestamp': self.data.index[self.current_index] # Use the timestamp from the data row
        }
        self.portfolio_manager.execute_trade(trade)

    def sell(self, quantity, price, commission=0):
        trade = {
            'symbol': self.symbol,
            'type': 'sell',
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'timestamp': self.data.index[self.current_index] # Use the timestamp from the data row
        }
        self.portfolio_manager.execute_trade(trade)


