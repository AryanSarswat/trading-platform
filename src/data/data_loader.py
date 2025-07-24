import pandas as pd
import os
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
    """
    Handles loading historical financial data from various sources.
    """
    def __init__(self, data_path: str):
        """
        Initializes the DataLoader with the path to the data directory.

        Args:
            data_path: The absolute path to the directory containing data files.
        """
        self.data_path = data_path

    def load_csv(self, file_name: str) -> Optional[pd.DataFrame]:
        """
        Loads data from a single CSV file.
        Assumes CSV has date as index and columns like 'Open', 'High', 'Low', 'Close', 'Volume'.
        Skips the first two rows which contain metadata.

        Args:
            file_name: The name of the CSV file to load.

        Returns:
            A pandas DataFrame containing the loaded data, or None if an error occurs.
        """
        full_path = os.path.join(self.data_path, file_name)
        try:
            # Skip the first two rows and read the 'Date' column as index
            df = pd.read_csv(full_path, index_col=0, parse_dates=True, skiprows=[1, 2])
            logging.info(f"Successfully loaded data from {full_path}")
            return df
        except FileNotFoundError:
            logging.error(f"Error: File {full_path} not found.")
            return None
        except Exception as e:
            logging.error(f"An error occurred while loading {full_path}: {e}")
            return None

    def load_multiple_csvs(self, symbols: List[str]) -> Optional[pd.DataFrame]:
        """
        Loads data for multiple symbols from CSV files and combines them.

        Args:
            symbols: A list of ticker symbols (e.g., ["AAPL", "MSFT"]).

        Returns:
            A pandas DataFrame with combined data, or None if loading fails.
            Columns will be renamed to include the symbol (e.g., 'Close_AAPL').
        """
        combined_df = pd.DataFrame()
        for symbol in symbols:
            file_name = f"{symbol}.csv"
            df = self.load_csv(file_name)
            if df is None:
                logging.warning(f"Could not load data for {symbol}. Skipping.")
                continue
            
            # Rename columns to include symbol
            df = df.add_suffix(f"_{symbol}")
            
            if combined_df.empty:
                combined_df = df
            else:
                combined_df = pd.merge(combined_df, df, left_index=True, right_index=True, how='outer')
        
        if combined_df.empty:
            logging.error("No data loaded for any of the symbols.")
            return None

        # Sort by index (Date) and forward fill any missing values introduced by merging
        combined_df = combined_df.sort_index().ffill()
        logging.info(f"Successfully loaded and combined data for symbols: {symbols}")
        return combined_df