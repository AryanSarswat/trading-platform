import numpy as np
import pandas as pd
from typing import List, Dict, Any

class PerformanceCalculator:
    """
    Calculates various performance metrics for a backtesting strategy.
    """
    def __init__(self, equity_curve: List[Dict[str, Any]], trades: List[Dict[str, Any]], closed_trades: List[Dict[str, Any]], risk_free_rate: float = 0.02):
        """
        Initializes the PerformanceCalculator.

        Args:
            equity_curve: A list of dictionaries representing the equity curve.
            trades: A list of dictionaries representing the trades.
            closed_trades: A list of dictionaries representing the closed trades with PnL.
            risk_free_rate: The risk-free rate of return.
        """
        self.equity_curve = pd.DataFrame(equity_curve).set_index("timestamp")
        self.equity_curve.index = pd.to_datetime(self.equity_curve.index)
        self.equity_curve["equity"] = pd.to_numeric(self.equity_curve["equity"])
        self.trades = trades
        self.closed_trades = closed_trades
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self) -> pd.Series:
        """
        Calculates daily returns from the equity curve.

        Returns:
            A pandas Series representing the daily returns.
        """
        self.equity_curve["returns"] = self.equity_curve["equity"].pct_change()
        return self.equity_curve["returns"]

    def sharpe_ratio(self) -> float:
        """
        Calculates the Sharpe Ratio.
        (Mean Return - Risk-Free Rate) / Standard Deviation of Returns

        Returns:
            The Sharpe Ratio.
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        annualized_returns = returns.mean() * 252
        annualized_std = returns.std() * np.sqrt(252)
        if annualized_std == 0:
            return 0.0
        return (annualized_returns - self.risk_free_rate) / annualized_std

    def sortino_ratio(self) -> float:
        """
        Calculates the Sortino Ratio.
        (Mean Return - Risk-Free Rate) / Downside Deviation

        Returns:
            The Sortino Ratio.
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        downside_returns = returns[returns < 0]
        if downside_returns.empty:
            return np.inf
        downside_std = downside_returns.std() * np.sqrt(252)
        annualized_returns = returns.mean() * 252
        if downside_std == 0 or np.isnan(downside_std):
            return 0.0
        return (annualized_returns - self.risk_free_rate) / downside_std

    def max_drawdown(self) -> float:
        """
        Calculates the Maximum Drawdown.

        Returns:
            The Maximum Drawdown.
        """
        if self.equity_curve.empty:
            return 0.0
        equity = self.equity_curve["equity"]
        peak = equity.expanding(min_periods=1).max()
        drawdown = (equity - peak) / peak
        return drawdown.min()

    def win_loss_ratio(self) -> float:
        """
        Calculates the Win/Loss Ratio based on closed trade PnL.

        Returns:
            The Win/Loss Ratio.
        """
        if not self.closed_trades:
            return 0.0

        wins = sum(1 for trade in self.closed_trades if trade['pnl'] > 0)
        losses = sum(1 for trade in self.closed_trades if trade['pnl'] <= 0)

        if losses == 0:
            return float("inf") if wins > 0 else 0.0
        return wins / losses

    def cagr(self) -> float:
        """
        Calculates the Compound Annual Growth Rate (CAGR).

        Returns:
            The CAGR.
        """
        if self.equity_curve.empty:
            return 0.0
        start_equity = self.equity_curve["equity"].iloc[0]
        end_equity = self.equity_curve["equity"].iloc[-1]
        
        if start_equity <= 0:
            return 0.0 # Avoid division by zero or negative base

        num_years = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days / 365.0
        if num_years <= 0:
            return 0.0
        
        # Handle negative returns gracefully
        if end_equity < start_equity:
            return (end_equity / start_equity - 1) / num_years # Linear approximation for negative CAGR
        else:
            return (end_equity / start_equity)**(1 / num_years) - 1

    def volatility(self) -> float:
        """
        Calculates the annualized volatility of returns.

        Returns:
            The annualized volatility.
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        return returns.std() * np.sqrt(252)

    def value_at_risk(self, confidence_level: float = 0.99) -> float:
        """
        Calculates the Historical Value at Risk (VaR).

        Args:
            confidence_level: The confidence level for VaR (e.g., 0.99 for 99% VaR).

        Returns:
            The VaR value.
        """
        returns = self.calculate_returns().dropna()
        if returns.empty:
            return 0.0
        
        # Sort returns in ascending order
        sorted_returns = returns.sort_values(ascending=True)
        
        # Calculate the index for the VaR
        var_index = int(len(sorted_returns) * (1 - confidence_level))
        
        # VaR is the return at this index
        var = abs(sorted_returns.iloc[var_index])
        
        return var

    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generates a dictionary containing all calculated performance metrics.

        Returns:
            A dictionary containing the performance metrics.
        """
        report = {
            "Sharpe Ratio": self.sharpe_ratio(),
            "Sortino Ratio": self.sortino_ratio(),
            "Max Drawdown": self.max_drawdown(),
            "Win/Loss Ratio": self.win_loss_ratio(),
            "CAGR": self.cagr(),
            "Volatility": self.volatility(),
            "Value at Risk (99%)": self.value_at_risk(0.99),
            "Initial Cash": self.equity_curve["equity"].iloc[0] if not self.equity_curve.empty else 0.0,
            "Final Equity": self.equity_curve["equity"].iloc[-1] if not self.equity_curve.empty else 0.0,
            "Total Trades": len(self.trades)
        }
        return report


