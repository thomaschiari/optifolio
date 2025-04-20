import polars as pl
import yfinance as yf
from typing import List, Optional

class DataLoader:
    """
    Object to load stock data from Yahoo Finance.

    Attributes:
        tickers (List[str]): List of stock tickers to load data for.
        start_date (str): Start date to load data from.
        end_date (str): End date to load data to.
        interval (str): Interval to load data at.
        prices_df (Optional[pl.DataFrame]): DataFrame containing adjusted close prices.
        returns_df (Optional[pl.DataFrame]): DataFrame containing daily returns.
    """

    def __init__(self, tickers: List[str], start_date: str, end_date: str, interval: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.prices_df = None
        self.returns_df = None

    def fetch_data(self) -> pl.DataFrame:
        """
        Fetch stock data from Yahoo Finance.

        Returns:
            pl.DataFrame: DataFrame containing stock data.
        """
        # Use yfinance to download data
        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            interval=self.interval
        )["Adj Close"]
        
        # Convert to Polars DataFrame
        self.prices_df = pl.from_pandas(data)
        return self.prices_df

    def compute_daily_returns(self) -> pl.DataFrame:
        """
        Compute daily returns from adjusted close prices.

        Returns:
            pl.DataFrame: DataFrame containing daily returns.
        """
        if self.prices_df is None:
            raise ValueError("No price data available. Call fetch_data() first.")
        
        # Calculate daily returns using Polars
        self.returns_df = self.prices_df.pct_change().drop_nulls()
        return self.returns_df

    def save_prices_to_csv(self, filename: str):
        """
        Save adjusted close prices to a CSV file.
        
        Args:
            filename (str): Path to save the CSV file.
        """
        if self.prices_df is None:
            raise ValueError("No price data available. Call fetch_data() first.")
        
        self.prices_df.write_csv(filename)
        print(f"Price data saved to {filename}")

    def save_returns_to_csv(self, filename: str):
        """
        Save daily returns to a CSV file.
        
        Args:
            filename (str): Path to save the CSV file.
        """
        if self.returns_df is None:
            raise ValueError("No returns data available. Call compute_daily_returns() first.")
        
        self.returns_df.write_csv(filename)
        print(f"Returns data saved to {filename}")

    def load_prices_from_csv(self, filename: str):
        """
        Load adjusted close prices from a CSV file.
        
        Args:
            filename (str): Path to the CSV file.
        """
        self.prices_df = pl.read_csv(filename)
        print(f"Price data loaded from {filename}")

    def load_returns_from_csv(self, filename: str):
        """
        Load daily returns from a CSV file.
        
        Args:
            filename (str): Path to the CSV file.
        """
        self.returns_df = pl.read_csv(filename)
        print(f"Returns data loaded from {filename}")
        
        
        

        
