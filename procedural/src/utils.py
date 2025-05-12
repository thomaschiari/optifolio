import numpy as np
import pandas as pd
from typing import Sequence

class PortfolioMetrics:
    """
    Helper functions to compute portfolio metrics.
    """

    @staticmethod
    def compute_portfolio_returns(
        weights: Sequence[float],
        returns: pd.DataFrame
    ) -> np.ndarray:
        """
        Compute portfolio returns given prices and weights:
        return = weights @ returns

        Args:
            weights (Sequence[float]): List of weights for each stock.
            returns (pd.DataFrame): DataFrame containing daily returns.

        Returns:
            np.ndarray: Array containing portfolio returns.
        """
        # Convert weights to numpy array
        weights_array = np.array(weights)
        
        # Ensure weights sum to 1
        if not np.isclose(np.sum(weights_array), 1.0):
            raise ValueError("Weights must sum to 1.0")
        
        # Convert DataFrame to numpy array for matrix multiplication
        returns_array = returns.values
        
        # Compute portfolio returns using matrix multiplication
        portfolio_returns = returns_array.dot(weights_array)
        
        return portfolio_returns

    @staticmethod
    def annualized_return(
        returns: Sequence[float],
        trading_days: int = 252
    ) -> float:
        """
        Compute annualized return given daily returns.
        R_ann = avg(R_daily) * trading_days

        Args:
            returns (Sequence[float]): List of daily returns.
            trading_days (int): Number of trading days in a year.

        Returns:
            float: Annualized return.
        """
        # Convert returns to numpy array
        returns_array = np.array(returns)
        
        # Calculate average daily return
        avg_daily_return = np.mean(returns_array)
        
        # Calculate annualized return
        annualized_return = avg_daily_return * trading_days
        
        return annualized_return

    @staticmethod
    def compute_portfolio_annualized_volatility(
        returns: Sequence[float],
        trading_days: int = 252
    ) -> float:
        """
        Compute annualized volatility given daily returns.
        sigma_ann = sqrt(trading_days) * std(R_daily)

        Args:
            returns (Sequence[float]): List of daily returns.
            trading_days (int): Number of trading days in a year.

        Returns:
            float: Annualized volatility.
        """
        # Convert returns to numpy array
        returns_array = np.array(returns)
        
        # Calculate daily volatility (standard deviation)
        daily_volatility = np.std(returns_array)
        
        # Calculate annualized volatility
        annualized_volatility = daily_volatility * np.sqrt(trading_days)
        
        return annualized_volatility

    @staticmethod
    def compute_portfolio_sharpe_ratio(
        returns: Sequence[float],
        risk_free_rate: float = 0.0
    ) -> float:
        """
        Compute Sharpe ratio given daily returns.
        SR = (R_p - R_f) / sigma_p

        Args:
            returns (Sequence[float]): List of daily returns.
            risk_free_rate (float): Risk-free rate.

        Returns:
            float: Sharpe ratio.
        """
        # Convert returns to numpy array
        returns_array = np.array(returns)
        
        # Calculate average daily return
        avg_daily_return = np.mean(returns_array)
        
        # Calculate daily volatility (standard deviation)
        daily_volatility = np.std(returns_array)
        
        # Calculate Sharpe ratio
        if daily_volatility == 0:
            return 0.0  # Avoid division by zero
            
        sharpe_ratio = (avg_daily_return - risk_free_rate) / daily_volatility
        
        return sharpe_ratio