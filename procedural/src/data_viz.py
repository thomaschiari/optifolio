import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
import numpy as np
import polars as pl
from typing import List, Dict, Any, Optional, Tuple

class DataViz:
    """
    Class for creating visualizations of stock data and portfolio simulations.
    
    This class provides methods to create interactive visualizations using Plotly
    for stock price data, returns, portfolio performance, and simulation results.
    """
    
    @staticmethod
    def plot_stock_prices(prices_df: pl.DataFrame, title: str = "Stock Prices Over Time") -> go.Figure:
        """
        Create a line plot of stock prices over time.
        
        Args:
            prices_df (pl.DataFrame): DataFrame containing stock prices.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = prices_df.to_pandas()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each stock
        for column in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[column],
                name=column,
                mode='lines'
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def plot_stock_returns(returns_df: pl.DataFrame, title: str = "Daily Returns") -> go.Figure:
        """
        Create a line plot of daily returns.
        
        Args:
            returns_df (pl.DataFrame): DataFrame containing daily returns.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = returns_df.to_pandas()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each stock
        for column in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[column],
                name=column,
                mode='lines'
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Return",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def plot_returns_distribution(returns_df: pl.DataFrame, title: str = "Returns Distribution") -> go.Figure:
        """
        Create a histogram of returns for each stock.
        
        Args:
            returns_df (pl.DataFrame): DataFrame containing daily returns.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = returns_df.to_pandas()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each stock
        for column in df.columns:
            fig.add_trace(go.Histogram(
                x=df[column],
                name=column,
                nbinsx=50,
                opacity=0.7
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Return",
            yaxis_title="Frequency",
            barmode='overlay',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def plot_correlation_heatmap(returns_df: pl.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
        """
        Create a correlation heatmap of returns.
        
        Args:
            returns_df (pl.DataFrame): DataFrame containing daily returns.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = returns_df.to_pandas()
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Stock",
            yaxis_title="Stock",
            height=800,
            width=800
        )
        
        return fig
    
    @staticmethod
    def plot_portfolio_performance(
        weights: List[float],
        returns_df: pl.DataFrame,
        tickers: List[str],
        title: str = "Portfolio Performance"
    ) -> go.Figure:
        """
        Create a plot of portfolio performance over time.
        
        Args:
            weights (List[float]): Portfolio weights.
            returns_df (pl.DataFrame): DataFrame containing daily returns.
            tickers (List[str]): List of tickers in the portfolio.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Select only the tickers in the portfolio
        portfolio_returns = returns_df.select(tickers)
        
        # Convert to numpy for calculations
        returns_array = portfolio_returns.to_numpy()
        weights_array = np.array(weights)
        
        # Calculate portfolio returns
        portfolio_returns = returns_array.dot(weights_array)
        
        # Calculate cumulative returns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        # Create figure
        fig = go.Figure()
        
        # Add trace for portfolio
        fig.add_trace(go.Scatter(
            x=returns_df.index,
            y=cumulative_returns,
            name="Portfolio",
            mode='lines',
            line=dict(color='blue', width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            hovermode="x unified"
        )
        
        return fig
    
    @staticmethod
    def plot_portfolio_weights(
        weights: List[float],
        tickers: List[str],
        title: str = "Portfolio Weights"
    ) -> go.Figure:
        """
        Create a bar chart of portfolio weights.
        
        Args:
            weights (List[float]): Portfolio weights.
            tickers (List[str]): List of tickers in the portfolio.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Create figure
        fig = go.Figure()
        
        # Add trace for weights
        fig.add_trace(go.Bar(
            x=tickers,
            y=weights,
            text=[f"{w:.2%}" for w in weights],
            textposition='auto',
        ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Stock",
            yaxis_title="Weight",
            yaxis=dict(tickformat=".0%"),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def plot_simulation_results(
        simulation_results: pl.DataFrame,
        title: str = "Portfolio Simulation Results"
    ) -> go.Figure:
        """
        Create a scatter plot of simulation results.
        
        Args:
            simulation_results (pl.DataFrame): DataFrame containing simulation results.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = simulation_results.to_pandas()
        
        # Create figure
        fig = go.Figure()
        
        # Add trace for simulation results
        fig.add_trace(go.Scatter(
            x=df['annualized_volatility'],
            y=df['annualized_return'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['sharpe_ratio'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Sharpe Ratio')
            ),
            text=[f"Sharpe: {sr:.2f}" for sr in df['sharpe_ratio']],
            hoverinfo='text'
        ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Annualized Volatility",
            yaxis_title="Annualized Return",
            hovermode="closest"
        )
        
        return fig
    
    @staticmethod
    def plot_efficient_frontier(
        simulation_results: pl.DataFrame,
        title: str = "Efficient Frontier"
    ) -> go.Figure:
        """
        Create a plot of the efficient frontier.
        
        Args:
            simulation_results (pl.DataFrame): DataFrame containing simulation results.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Convert to pandas for easier plotting with Plotly
        df = simulation_results.to_pandas()
        
        # Sort by volatility
        df = df.sort_values('annualized_volatility')
        
        # Create figure
        fig = go.Figure()
        
        # Add trace for efficient frontier
        fig.add_trace(go.Scatter(
            x=df['annualized_volatility'],
            y=df['annualized_return'],
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='blue', width=2)
        ))
        
        # Add trace for all portfolios
        fig.add_trace(go.Scatter(
            x=df['annualized_volatility'],
            y=df['annualized_return'],
            mode='markers',
            marker=dict(
                size=8,
                color=df['sharpe_ratio'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Sharpe Ratio')
            ),
            name='Portfolios',
            text=[f"Sharpe: {sr:.2f}" for sr in df['sharpe_ratio']],
            hoverinfo='text'
        ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Annualized Volatility",
            yaxis_title="Annualized Return",
            hovermode="closest"
        )
        
        return fig
    
    @staticmethod
    def plot_portfolio_comparison(
        portfolios: Dict[str, Tuple[List[float], List[str]]],
        returns_df: pl.DataFrame,
        title: str = "Portfolio Comparison"
    ) -> go.Figure:
        """
        Create a plot comparing multiple portfolios.
        
        Args:
            portfolios (Dict[str, Tuple[List[float], List[str]]]): Dictionary of portfolios.
                Keys are portfolio names, values are tuples of (weights, tickers).
            returns_df (pl.DataFrame): DataFrame containing daily returns.
            title (str): Title for the plot.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        # Create figure
        fig = go.Figure()
        
        # Add trace for each portfolio
        for name, (weights, tickers) in portfolios.items():
            # Select only the tickers in the portfolio
            portfolio_returns = returns_df.select(tickers)
            
            # Convert to numpy for calculations
            returns_array = portfolio_returns.to_numpy()
            weights_array = np.array(weights)
            
            # Calculate portfolio returns
            portfolio_returns = returns_array.dot(weights_array)
            
            # Calculate cumulative returns
            cumulative_returns = (1 + portfolio_returns).cumprod()
            
            # Add trace
            fig.add_trace(go.Scatter(
                x=returns_df.index,
                y=cumulative_returns,
                name=name,
                mode='lines'
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
