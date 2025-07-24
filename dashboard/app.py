import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

from src.backtesting.engine import BacktestingEngine
from src.strategies.moving_average_crossover import MovingAverageCrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.mean_reversion import MeanReversion
from src.strategies.lstm_strategy import LSTMStrategy
from src.strategies.pairs_trading_strategy import PairsTradingStrategy
from src.reporting.performance import PerformanceCalculator
from src.data.data_loader import DataLoader

# --- Configuration --- #
REPORTS_DIR = "reports"
BACKTEST_RESULTS_FILE = os.path.join(REPORTS_DIR, "backtest_results.json")
PERFORMANCE_SUMMARY_FILE = os.path.join(REPORTS_DIR, "performance_summary.json")
DATA_PATH = "data"

# Map strategy names to classes
STRATEGY_MAPPING = {
    "moving_average_crossover": MovingAverageCrossover,
    "rsi_strategy": RSIStrategy,
    "mean_reversion": MeanReversion,
    "lstm_strategy": LSTMStrategy,
    "pairs_trading_strategy": PairsTradingStrategy
}


st.set_page_config(layout="wide", page_title="Quant Trading Backtesting Dashboard")

# --- Helper Functions --- #
@st.cache_data
def load_results():
    if not os.path.exists(BACKTEST_RESULTS_FILE):
        st.error(f"Backtest results file not found: {BACKTEST_RESULTS_FILE}")
        return {}, {}
    if not os.path.exists(PERFORMANCE_SUMMARY_FILE):
        st.error(f"Performance summary file not found: {PERFORMANCE_SUMMARY_FILE}")
        return {}, {}

    with open(BACKTEST_RESULTS_FILE, 'r') as f:
        all_results = json.load(f)
    with open(PERFORMANCE_SUMMARY_FILE, 'r') as f:
        performance_summaries = json.load(f)
    return all_results, performance_summaries

def plot_equity_curve(equity_curve_df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=equity_curve_df.index, y=equity_curve_df["equity"], mode='lines', name='Equity Curve'))
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Equity',
        hovermode="x unified",
        template="plotly_dark"
    )
    return fig

def run_live_simulation(strategy_name, strategy_params, symbols, initial_cash):
    st.subheader(f"Live Simulation for {strategy_name} on {symbols}")
    
    data_loader = DataLoader(DATA_PATH)
    data = data_loader.load_multiple_csvs(symbols)

    if data is None or data.empty:
        st.error(f"Could not load data for {symbols}. Cannot run live simulation.")
        return

    engine = BacktestingEngine(initial_cash=initial_cash, data_path=DATA_PATH)
    
    # Special handling for PairsTradingStrategy symbols
    if strategy_name == "PairsTradingStrategy":
        strategy = STRATEGY_MAPPING[strategy_name](symbol1=symbols[0], symbol2=symbols[1], **strategy_params)
    else:
        strategy = STRATEGY_MAPPING[strategy_name](symbol=symbols[0], **strategy_params)

    engine.set_strategy(strategy)

    equity_curve_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    equity_data = []

    for i, (index, row) in enumerate(data.iterrows()):
        current_prices = {}
        for col in data.columns:
            if col.startswith("Close_"):
                symbol = col.replace("Close_", "")
                current_prices[symbol] = row[col]

        engine.portfolio_manager.update_portfolio(current_prices, index)
        if hasattr(strategy, 'symbol') and strategy.symbol in current_prices:
            strategy.check_stop_loss(current_prices[strategy.symbol])
        strategy.on_bar(i, row)

        equity_data.append({'timestamp': index, 'equity': engine.portfolio_manager.equity_curve[-1]['equity']})
        equity_df = pd.DataFrame(equity_data).set_index("timestamp")

        with equity_curve_placeholder.container():
            st.plotly_chart(plot_equity_curve(equity_df, f"Live Equity Curve - {strategy_name} on {symbols}"), use_container_width=True)
        
        with metrics_placeholder.container():
            current_metrics = {
                "Current Cash": engine.portfolio_manager.cash,
                "Current Equity": engine.portfolio_manager.equity_curve[-1]['equity'],
                "Open Positions": {s: p['quantity'] for s, p in engine.portfolio_manager.positions.items()}
            }
            st.json(current_metrics)

        time.sleep(0.1) # Simulate real-time delay

    st.success("Live simulation finished!")
    final_calculator = PerformanceCalculator(engine.portfolio_manager.equity_curve, engine.portfolio_manager.trades, engine.portfolio_manager.closed_trades)
    st.subheader("Final Performance Report")
    st.table(pd.DataFrame([final_calculator.generate_performance_report()]).T.rename(columns={0: "Value"}))

# --- Main Dashboard Layout --- #
st.title("Quant Trading Backtesting Dashboard")

all_results, performance_summaries = load_results()

if not all_results or not performance_summaries:
    st.warning("No backtest results found. Please run backtests first using `scripts/run_backtest.py`.")
else:
    st.sidebar.header("Select Options")
    
    mode = st.sidebar.radio("Choose Mode", ["View Backtest Results", "Run Live Simulation"])

    if mode == "View Backtest Results":
        selected_ticker_or_pair = st.sidebar.selectbox(
            "Select Ticker or Pair",
            list(all_results.keys())
        )

        if selected_ticker_or_pair:
            strategies_for_selection = list(all_results[selected_ticker_or_pair].keys())
            selected_strategy = st.sidebar.selectbox(
                "Select Strategy",
                strategies_for_selection
            )

            if selected_strategy:
                st.header(f"Results for {selected_strategy} on {selected_ticker_or_pair}")

                # Display Performance Metrics
                st.subheader("Performance Metrics")
                metrics = performance_summaries[selected_ticker_or_pair][selected_strategy]
                metrics_df = pd.DataFrame([metrics]).T.rename(columns={0: "Value"})
                st.table(metrics_df)

                # Plot Equity Curve
                st.subheader("Equity Curve")
                equity_curve_json = all_results[selected_ticker_or_pair][selected_strategy]["equity_curve"]
                equity_curve_df = pd.DataFrame(
                    data=json.loads(equity_curve_json)["data"],
                    index=pd.to_datetime(json.loads(equity_curve_json)["index"], unit="ms"),
                    columns=json.loads(equity_curve_json)["columns"]
                )
                fig = plot_equity_curve(equity_curve_df, f'{selected_ticker_or_pair} - {selected_strategy} Equity Curve')
                st.plotly_chart(fig, use_container_width=True)

    elif mode == "Run Live Simulation":
        st.sidebar.subheader("Simulation Settings")
        
        # Get all available symbols from backtest results
        all_symbols = set()
        for key in all_results.keys():
            if '-' in key: # Pairs trading
                all_symbols.update(key.split('-'))
            else:
                all_symbols.add(key)
        all_symbols = sorted(list(all_symbols))

        # Allow selection of symbols for simulation
        selected_sim_symbols = st.sidebar.multiselect(
            "Select Symbols for Simulation",
            all_symbols,
            default=all_symbols[0] if all_symbols else []
        )

        if len(selected_sim_symbols) > 2:
            st.warning("Please select up to 2 symbols for live simulation.")
        elif len(selected_sim_symbols) == 0:
            st.info("Please select at least one symbol to run simulation.")
        else:
            # Dynamically create strategy options based on selected symbols
            available_strategies = []
            if len(selected_sim_symbols) == 1:
                available_strategies = [s for s in STRATEGY_MAPPING.keys() if s != "pairs_trading_strategy"]
            elif len(selected_sim_symbols) == 2:
                available_strategies = [s for s in STRATEGY_MAPPING.keys() if s == "pairs_trading_strategy"]
            
            if not available_strategies:
                st.warning("No suitable strategy found for selected symbols.")
            else:
                selected_sim_strategy_name = st.sidebar.selectbox(
                    "Select Strategy for Simulation",
                    available_strategies
                )

                if selected_sim_strategy_name:
                    # Get default params from config.yml (assuming first entry for strategy)
                    default_params = {}
                    for strat_conf in CONFIG['strategies']:
                        if selected_sim_strategy_name in strat_conf:
                            default_params = strat_conf[selected_sim_strategy_name]
                            break

                    st.sidebar.json(default_params) # Display default params

                    if st.sidebar.button("Start Live Simulation"):
                        run_live_simulation(selected_sim_strategy_name, default_params, selected_sim_symbols, CONFIG['backtest']['initial_cash'])


    st.sidebar.markdown("""
    --- 
    **How to use:**
    1. Run backtests: `python scripts/run_backtest.py`
    2. Refresh this page.
    3. For live simulation, select symbols and a strategy, then click 'Start Live Simulation'.
    """)