import pandas as pd
import yfinance as yf
from typing import List, Optional
import time
from datetime import datetime

class DataLoader:
    """
    Object to load stock data from Yahoo Finance.

    Attributes:
        tickers (List[str]): List of stock tickers to load data for.
        start_date (str): Start date to load data from.
        end_date (str): End date to load data to.
        interval (str): Interval to load data at.
        prices_df (Optional[pd.DataFrame]): DataFrame containing adjusted close prices.
        returns_df (Optional[pd.DataFrame]): DataFrame containing daily returns.
    """

    def __init__(self, tickers: List[str], start_date: str, end_date: str, interval: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.prices_df = None
        self.returns_df = None

    def fetch_data(self, batch_size: int = 1, delay: float = 1.0) -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance with rate limiting.

        Args:
            batch_size (int): Number of tickers to fetch in each batch.
            delay (float): Delay in seconds between batches to avoid rate limiting.

        Returns:
            pd.DataFrame: DataFrame containing stock data.
        """
        all_data = []
        
        # Process tickers in batches
        for i in range(0, len(self.tickers), batch_size):
            batch_tickers = self.tickers[i:i + batch_size]
            print(f"Fetching data for tickers: {batch_tickers}")
            
            try:
                # Download data for the current batch
                batch_data = yf.download(
                    batch_tickers,
                    start=self.start_date,
                    end=self.end_date,
                    interval=self.interval,
                    progress=False
                )["Adj Close"]
                
                all_data.append(batch_data)
                
                # Add delay between batches to avoid rate limiting
                if i + batch_size < len(self.tickers):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"Error fetching data for batch {batch_tickers}: {str(e)}")
                continue
        
        # Combine all batches
        if all_data:
            self.prices_df = pd.concat(all_data, axis=1)
            return self.prices_df
        else:
            raise ValueError("No data was successfully fetched")

    def compute_daily_returns(self) -> pd.DataFrame:
        """
        Compute daily returns from adjusted close prices.

        Returns:
            pd.DataFrame: DataFrame containing daily returns.
        """
        if self.prices_df is None:
            raise ValueError("No price data available. Call fetch_data() first.")
        
        # Calculate daily returns using Pandas
        self.returns_df = self.prices_df.pct_change()
        return self.returns_df

    def save_prices_to_csv(self, filename: str):
        """
        Save adjusted close prices to a CSV file.
        
        Args:
            filename (str): Path to save the CSV file.
        """
        if self.prices_df is None:
            raise ValueError("No price data available. Call fetch_data() first.")
        
        self.prices_df.to_csv(filename)
        print(f"Price data saved to {filename}")

    def save_returns_to_csv(self, filename: str):
        """
        Save daily returns to a CSV file.
        
        Args:
            filename (str): Path to save the CSV file.
        """
        if self.returns_df is None:
            raise ValueError("No returns data available. Call compute_daily_returns() first.")
        
        self.returns_df.to_csv(filename)
        print(f"Returns data saved to {filename}")

    def load_prices_from_csv(self, filename: str):
        """
        Load adjusted close prices from a CSV file.
        
        Args:
            filename (str): Path to the CSV file.
        """
        self.prices_df = pd.read_csv(filename, index_col=0, parse_dates=True)
        print(f"Price data loaded from {filename}")

    def load_returns_from_csv(self, filename: str):
        """
        Load daily returns from a CSV file.
        
        Args:
            filename (str): Path to the CSV file.
        """
        self.returns_df = pd.read_csv(filename, index_col=0, parse_dates=True)
        print(f"Returns data loaded from {filename}")
        
        
        

        
