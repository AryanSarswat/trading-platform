import yfinance as yf
import os

def download_data(ticker, start_date, end_date, output_dir):
    """
    Downloads historical stock data using yfinance and saves it to a CSV file.
    """
    try:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data = yf.download(ticker, start=start_date, end=end_date)
        output_path = os.path.join(output_dir, f"{ticker}.csv")
        data.to_csv(output_path)
        print(f"Successfully downloaded {ticker} data to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading {ticker} data: {e}")
        return None

if __name__ == "__main__":
    # Corrected path to be relative to the project's data directory
    output_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    # Download AAPL data
    download_data("AAPL", "2020-01-01", "2023-12-31", output_directory)

    # Download MSFT data
    download_data("MSFT", "2020-01-01", "2023-12-31", output_directory)

    # Download GOOGL data
    download_data("GOOGL", "2020-01-01", "2023-12-31", output_directory)


