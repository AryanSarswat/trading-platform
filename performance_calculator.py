import numpy as np
import pandas as pd

class PerformanceCalculator:
    """
    Calculates various performance metrics for a backtesting strategy.
    """
    def __init__(self, equity_curve, trades, risk_free_rate=0.02):
        self.equity_curve = pd.DataFrame(equity_curve).set_index("timestamp")
        self.equity_curve["equity"] = pd.to_numeric(self.equity_curve["equity"])
        self.trades = trades
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self):
        """
        Calculates daily returns from the equity curve.
        """
        self.equity_curve["returns"] = self.equity_curve["equity"].pct_change()
        return self.equity_curve["returns"]

    def sharpe_ratio(self):
        """
        Calculates the Sharpe Ratio.
        (Mean Return - Risk-Free Rate) / Standard Deviation of Returns
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        annualized_returns = returns.mean() * 252  # Assuming 252 trading days in a year
        annualized_std = returns.std() * np.sqrt(252)
        if annualized_std == 0:
            return 0.0
        return (annualized_returns - self.risk_free_rate) / annualized_std

    def sortino_ratio(self):
        """
        Calculates the Sortino Ratio.
        (Mean Return - Risk-Free Rate) / Downside Deviation
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        downside_returns = returns[returns < 0]
        if downside_returns.empty:
            return np.inf  # No downside risk
        downside_std = downside_returns.std() * np.sqrt(252)
        annualized_returns = returns.mean() * 252
        if downside_std == 0:
            return 0.0
        return (annualized_returns - self.risk_free_rate) / downside_std

    def max_drawdown(self):
        """
        Calculates the Maximum Drawdown.
        """
        if self.equity_curve.empty:
            return 0.0
        equity = self.equity_curve["equity"]
        peak = equity.expanding(min_periods=1).max()
        drawdown = (equity - peak) / peak
        return drawdown.min()

    def win_loss_ratio(self):
        """
        Calculates the Win/Loss Ratio.
        """
        if not self.trades:
            return 0.0

        wins = 0
        losses = 0

        # This is a simplified win/loss calculation. A more robust one would track individual trade PnL.
        # For now, we'll assume a 'win' if the equity curve increased from the previous point.
        returns = self.calculate_returns().dropna()
        wins = (returns > 0).sum()
        losses = (returns < 0).sum()

        if losses == 0:
            return float("inf") if wins > 0 else 0.0
        return wins / losses

    def cagr(self):
        """
        Calculates the Compound Annual Growth Rate (CAGR).
        """
        if self.equity_curve.empty:
            return 0.0
        start_equity = self.equity_curve["equity"].iloc[0]
        end_equity = self.equity_curve["equity"].iloc[-1]
        num_years = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days / 365.25
        if num_years <= 0:
            return 0.0
        return (end_equity / start_equity)**(1 / num_years) - 1

    def volatility(self):
        """
        Calculates the annualized volatility of returns.
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        return returns.std() * np.sqrt(252)

    def generate_performance_report(self):
        """
        Generates a dictionary containing all calculated performance metrics.
        """
        report = {
            "Sharpe Ratio": self.sharpe_ratio(),
            "Sortino Ratio": self.sortino_ratio(),
            "Max Drawdown": self.max_drawdown(),
            "Win/Loss Ratio": self.win_loss_ratio(),
            "CAGR": self.cagr(),
            "Volatility": self.volatility(),
            "Initial Cash": self.equity_curve["equity"].iloc[0] if not self.equity_curve.empty else self.risk_free_rate, # Using risk_free_rate as a placeholder if equity_curve is empty
            "Final Equity": self.equity_curve["equity"].iloc[-1] if not self.equity_curve.empty else self.risk_free_rate, # Using risk_free_rate as a placeholder if equity_curve is empty
            "Total Trades": len(self.trades)
        }
        return report


