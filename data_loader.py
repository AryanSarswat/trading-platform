import pandas as pd
import os

class DataLoader:
    """
    Handles loading historical financial data from various sources.
    """
    def __init__(self, data_path):
        self.data_path = data_path

    def load_csv(self, file_name):
        """
        Loads data from a CSV file.
        Assumes CSV has date as index and columns like 'Open', 'High', 'Low', 'Close', 'Volume'.
        Skips the first two rows which contain metadata.
        """
        full_path = os.path.join(self.data_path, file_name)
        try:
            # Skip the first two rows and read the 'Date' column as index
            df = pd.read_csv(full_path, index_col=0, parse_dates=True, skiprows=[1, 2])
            print(f"Successfully loaded data from {full_path}")
            return df
        except FileNotFoundError:
            print(f"Error: File {full_path} not found.")
            return None
        except Exception as e:
            print(f"An error occurred while loading {full_path}: {e}")
            return None


