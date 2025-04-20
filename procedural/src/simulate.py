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
        weights = np.random.dirichlet(np.ones(n_assets))
        return weights / sum(weights)
    
    def _apply_max_weight_constraint(self, weights: np.ndarray) -> np.ndarray:
        """
        Apply maximum weight constraint to the portfolio weights.
        
        Args:
            weights (np.ndarray): Original portfolio weights.
            
        Returns:
            np.ndarray: Adjusted weights that respect the maximum weight constraint.
        """
        # If max_weight is 1.0 or greater, no constraint needed
        if self.max_weight >= 1.0:
            return weights
            
        # Create a copy of the weights to avoid modifying the original
        adjusted_weights = weights.copy()
        
        # Find weights that exceed the maximum
        excess_mask = adjusted_weights > self.max_weight
        excess_weights = adjusted_weights[excess_mask]
        
        # If no weights exceed the maximum, return the original weights
        if not np.any(excess_mask):
            return adjusted_weights
            
        # Calculate the total excess weight
        total_excess = np.sum(excess_weights) - self.max_weight * np.sum(excess_mask)
        
        # Cap the weights that exceed the maximum
        adjusted_weights[excess_mask] = self.max_weight
        
        # Find weights that are below the maximum
        below_max_mask = ~excess_mask
        below_max_weights = adjusted_weights[below_max_mask]
        
        # If there are no weights below the maximum, we need to redistribute
        if not np.any(below_max_mask):
            # In this case, we need to set all weights to max_weight
            # and then normalize to ensure they sum to 1
            adjusted_weights = np.ones_like(adjusted_weights) * self.max_weight
            return adjusted_weights / np.sum(adjusted_weights)
            
        # Calculate the sum of weights below the maximum
        sum_below_max = np.sum(below_max_weights)
        
        # Redistribute the excess weight proportionally to weights below the maximum
        if sum_below_max > 0:
            redistribution_factor = total_excess / sum_below_max
            adjusted_weights[below_max_mask] += below_max_weights * redistribution_factor
            
        # Normalize to ensure weights sum to 1
        return adjusted_weights / np.sum(adjusted_weights)
    
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
            weights = self._apply_max_weight_constraint(weights)    
            
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