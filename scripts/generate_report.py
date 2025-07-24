import json
from tabulate import tabulate

import os

reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
performance_summary_file = os.path.join(reports_dir, "performance_summary.json")

with open(performance_summary_file, 'r') as f:
    performance_data = json.load(f)

headers = ["Ticker", "Strategy", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown", "Win/Loss Ratio", "CAGR", "Volatility", "Final Equity", "Total Trades"]
rows = []

for ticker, strategies in performance_data.items():
    for strategy_name, metrics in strategies.items():
        rows.append([
            ticker,
            strategy_name,
            f"{metrics['Sharpe Ratio']:.4f}",
            f"{metrics['Sortino Ratio']:.4f}",
            f"{metrics['Max Drawdown']:.4f}",
            f"{metrics['Win/Loss Ratio']:.4f}",
            f"{metrics['CAGR']:.4f}",
            f"{metrics['Volatility']:.4f}",
            f"{metrics['Final Equity']:.2f}",
            metrics['Total Trades']
        ])

table = tabulate(rows, headers=headers, tablefmt="pipe")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'performance_summary_table.md'), 'w') as f:
    f.write(table)


