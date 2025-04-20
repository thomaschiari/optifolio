import itertools
import numpy as np
import polars as pl
from typing import List, Tuple, Optional, Dict, Any
from joblib import Parallel, delayed
from utils import PortfolioMetrics

class PortfolioSimulator:
    """
    Simulate portfolio performance to maximize Sharpe ratio.  

    Attributes:
        returns (pl.DataFrame): DataFrame containing daily returns.
        risk_free_rate (float): Risk-free rate.
        num_simulations (int): Number of simulations to run.
        num_cores (int): Number of cores to use for parallel processing.
        tickers (List[str]): List of tickers to simulate.
        select_k_tickers (int): Number of tickers to select for each simulation.
        max_weight (float): Maximum weight for each ticker.
    """

    def __init__(
        self,
        returns: pl.DataFrame,
        risk_free_rate: float = 0.0,
        num_simulations: int = 1000,
        num_cores: int = 4,
        tickers: List[str] = None,
        select_k_tickers: int = 25,
        max_weight: float = 0.2
    ):
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.num_simulations = num_simulations
        self.num_cores = num_cores
        self.tickers = tickers
        self.select_k_tickers = select_k_tickers
        self.max_weight = max_weight

    def _generate_combinations(self) -> itertools.combinations:
        """
        Generate all possible combinations of tickers.

        Returns:
            itertools.combinations: All possible combinations of tickers.
        """
        return itertools.combinations(self.tickers, self.select_k_tickers)

    def _sample_weights(self, n_assets: int) -> np.ndarray:
        """
        Sample random weights for the portfolio.

        Args:
            n_assets (int): Number of assets in the portfolio.

        Returns:
            np.ndarray: Random weights for the portfolio.
        """
        # Generate random weights
        weights = np.random.random(n_assets)
        
        # Apply maximum weight constraint
        if self.max_weight < 1.0:
            # Scale down weights that exceed max_weight
            excess = np.maximum(weights - self.max_weight, 0)
            weights = np.minimum(weights, self.max_weight)
            
            # Redistribute excess weight proportionally to weights below max_weight
            available = 1.0 - np.sum(weights)
            if available > 0 and np.sum(excess) > 0:
                below_max = weights < self.max_weight
                if np.any(below_max):
                    weights[below_max] += (excess.sum() * weights[below_max] / np.sum(weights[below_max]))
        
        # Normalize weights to sum to 1
        weights = weights / np.sum(weights)
        
        return weights
    
    def _simulate_one(self, combo: Tuple[str, ...]) -> Dict[str, Any]:
        """
        Simulate the portfolio returns for a given combination of tickers.
        
        Args:
            combo (Tuple[str, ...]): Combination of tickers to simulate.
            
        Returns:
            Dict[str, Any]: Dictionary containing simulation results.
        """
        # Extract returns for the selected tickers
        selected_returns = self.returns.select(list(combo))
        
        # Run multiple simulations with different weights
        best_sharpe = -np.inf
        best_weights = None
        best_annualized_return = 0
        best_annualized_volatility = 0
        
        for _ in range(self.num_simulations):
            # Sample random weights
            weights = self._sample_weights(len(combo))
            
            # Compute portfolio returns
            portfolio_returns = PortfolioMetrics.compute_portfolio_returns(
                weights=weights,
                returns=selected_returns
            )
            
            # Compute metrics
            annualized_return = PortfolioMetrics.annualized_return(portfolio_returns)
            annualized_volatility = PortfolioMetrics.compute_portfolio_annualized_volatility(portfolio_returns)
            sharpe_ratio = PortfolioMetrics.compute_portfolio_sharpe_ratio(
                portfolio_returns,
                self.risk_free_rate
            )
            
            # Update best if current simulation is better
            if sharpe_ratio > best_sharpe:
                best_sharpe = sharpe_ratio
                best_weights = weights
                best_annualized_return = annualized_return
                best_annualized_volatility = annualized_volatility
        
        # Create result dictionary
        result = {
            'tickers': list(combo),
            'weights': best_weights.tolist(),
            'sharpe_ratio': best_sharpe,
            'annualized_return': best_annualized_return,
            'annualized_volatility': best_annualized_volatility
        }
        
        return result
    
    def run(self) -> pl.DataFrame:
        """
        Run the simulation.
        
        Returns:
            pl.DataFrame: DataFrame containing simulation results.
        """
        # Generate all possible combinations
        combinations = list(self._generate_combinations())
        
        # Run simulations in parallel
        results = Parallel(n_jobs=self.num_cores)(
            delayed(self._simulate_one)(combo) for combo in combinations
        )
        
        # Convert results to Polars DataFrame
        df_results = pl.DataFrame(results)
        
        # Sort by Sharpe ratio in descending order
        df_results = df_results.sort('sharpe_ratio', descending=True)
        
        return df_results