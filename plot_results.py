import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import io

def plot_equity_curve(equity_curve_json, title, output_path):
    equity_curve_data = json.loads(equity_curve_json)
    equity_curve_df = pd.DataFrame(
        data=equity_curve_data["data"],
        index=pd.to_datetime(equity_curve_data["index"], unit=\"ms\"),
        columns=equity_curve_data["columns"]
    )

    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve_df.index, equity_curve_df["equity"], label="Equity Curve")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved equity curve plot to {output_path}")

if __name__ == "__main__":
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    results_file = os.path.join(reports_dir, "backtest_results.json")

    with open(results_file, "r") as f:
        all_results = json.load(f)

    for ticker, strategies_results in all_results.items():
        for strategy_name, results in strategies_results.items():
            equity_curve_json = results["equity_curve"]
            plot_title = f"{ticker} - {strategy_name} Equity Curve"
            output_filename = f"{ticker}_{strategy_name}_equity_curve.png"
            output_path = os.path.join(reports_dir, output_filename)
            plot_equity_curve(equity_curve_json, plot_title, output_path)


