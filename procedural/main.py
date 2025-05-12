#!/usr/bin/env python3
"""
Optifolio - Portfolio Optimization

This script demonstrates the functionality of the Optifolio library for portfolio optimization.
"""

# Import required libraries
import sys
import time
import numpy as np
import pandas as pd
import plotly.io as pio
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Set Plotly to render in browser
pio.renderers.default = 'browser'

# Import Optifolio modules
from src import DataLoader, PortfolioSimulator, PortfolioMetrics, DataViz

def main():
    """Main function to demonstrate Optifolio functionality."""
    
    # 1. Load Stock Data
    print("1. Loading Stock Data...")
    
    # Define parameters
    tickers = [
        'MSFT', 'AAPL', 'NVDA', 'AMZN', 'WMT', 'JPM', 'V', 'HD', 'PG', 'JNJ',
        'UNH', 'KO', 'CRM', 'CVX', 'CSCO', 'IBM', 'MCD', 'AXP', 'MRK', 'DIS',
        'VZ', 'GS', 'CAT', 'BA', 'AMGN', 'HON', 'NKE', 'SHW', 'MMM', 'TRV'
    ]

    # Calculate date range (last 5 years)
    end_date = datetime(2024, 12, 31).strftime('%Y-%m-%d')
    start_date = datetime(2024, 8, 1).strftime('%Y-%m-%d')

    # Create DataLoader instance
    data_loader = DataLoader(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )

    # Fetch data
    print(f"Loading data for {len(tickers)} tickers from {start_date} to {end_date}...")
    prices_df = data_loader.fetch_data()
    print(f"Loaded {prices_df.shape[0]} days of price data.")

    # Compute daily returns
    returns_df = data_loader.compute_daily_returns()
    print(f"Computed {returns_df.shape[0]} days of returns data.")
    
    # 2. Visualize Stock Data
    print("\n2. Creating Stock Data Visualizations...")
    
    # Plot stock prices
    print("Generating stock prices plot...")
    fig_prices = DataViz.plot_stock_prices(prices_df, title="Stock Prices Over Time")
    fig_prices.show()
    
    # Plot stock returns
    print("Generating stock returns plot...")
    fig_returns = DataViz.plot_stock_returns(returns_df, title="Daily Returns")
    fig_returns.show()
    
    # Plot returns distribution
    print("Generating returns distribution plot...")
    fig_dist = DataViz.plot_returns_distribution(returns_df, title="Returns Distribution")
    fig_dist.show()
    
    # Plot correlation heatmap
    print("Generating correlation heatmap...")
    fig_corr = DataViz.plot_correlation_heatmap(returns_df, title="Correlation Heatmap")
    fig_corr.show()
    
    # 3. Run Portfolio Simulations
    print("\n3. Running Portfolio Simulations...")
    
    # Define simulation parameters
    risk_free_rate = 0.02  # 2% annual risk-free rate
    num_simulations = 1000  # Number of simulations per combination
    num_cores = 4  # Number of CPU cores to use
    select_k_tickers = 10  # Number of tickers to select for each portfolio
    max_weight = 0.3  # Maximum weight for each ticker

    # Create PortfolioSimulator instance
    simulator = PortfolioSimulator(
        returns=returns_df,
        risk_free_rate=risk_free_rate,
        num_simulations=num_simulations,
        num_cores=num_cores,
        tickers=tickers,
        select_k_tickers=select_k_tickers,
        max_weight=max_weight
    )

    # Run simulations and measure execution time
    print(f"Running simulations with {num_simulations} iterations per combination...")
    start_time = time.time()
    simulation_results = simulator.run()
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Simulation completed in {execution_time:.2f} seconds.")
    print(f"Found {simulation_results.shape[0]} optimal portfolios.")
    
    # 4. Visualize Simulation Results
    print("\n4. Creating Simulation Result Visualizations...")
    
    # Display top 5 portfolios
    print("Top 5 Portfolios:")
    top_portfolios = simulation_results.head(5)
    print(top_portfolios)
    
    # Plot simulation results
    print("Generating simulation results plot...")
    fig_sim = DataViz.plot_simulation_results(simulation_results, title="Portfolio Simulation Results")
    fig_sim.show()
    
    # Plot efficient frontier
    print("Generating efficient frontier plot...")
    fig_ef = DataViz.plot_efficient_frontier(simulation_results, title="Efficient Frontier")
    fig_ef.show()
    
    # 5. Analyze Best Portfolio
    print("\n5. Analyzing Best Portfolio...")
    
    # Get the best portfolio
    best_portfolio = simulation_results.iloc[0]
    best_tickers = best_portfolio['tickers']
    best_weights = best_portfolio['weights']
    best_sharpe = best_portfolio['sharpe_ratio']
    best_return = best_portfolio['annualized_return']
    best_volatility = best_portfolio['annualized_volatility']

    print(f"Best Portfolio:")
    print(f"Sharpe Ratio: {best_sharpe:.4f}")
    print(f"Annualized Return: {best_return:.2%}")
    print(f"Annualized Volatility: {best_volatility:.2%}")
    print("\nTickers and Weights:")
    for ticker, weight in zip(best_tickers, best_weights):
        print(f"{ticker}: {weight:.2%}")
    
    # Plot portfolio weights
    print("Generating portfolio weights plot...")
    fig_weights = DataViz.plot_portfolio_weights(best_weights, best_tickers, title="Best Portfolio Weights")
    fig_weights.show()
    
    # Plot portfolio performance
    print("Generating portfolio performance plot...")
    fig_perf = DataViz.plot_portfolio_performance(
        weights=best_weights,
        returns_df=returns_df,
        tickers=best_tickers,
        title="Best Portfolio Performance"
    )
    fig_perf.show()
    
    # 6. Compare with Equal-Weight Portfolio
    print("\n6. Comparing with Equal-Weight Portfolio...")
    
    # Create equal-weight portfolio
    equal_weights = [1/len(best_tickers)] * len(best_tickers)

    # Create portfolios dictionary for comparison
    portfolios = {
        'Optimized': (best_weights, best_tickers),
        'Equal-Weight': (equal_weights, best_tickers)
    }

    # Plot portfolio comparison
    print("Generating portfolio comparison plot...")
    fig_comp = DataViz.plot_portfolio_comparison(
        portfolios=portfolios,
        returns_df=returns_df,
        title="Portfolio Comparison"
    )
    fig_comp.show()
    
    # 7. Performance Analysis
    print("\n7. Analyzing Performance...")
    
    # Calculate performance metrics
    print(f"Simulation Performance:")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"Number of Portfolios: {simulation_results.shape[0]}")
    print(f"Simulations per Portfolio: {num_simulations}")
    print(f"Total Simulations: {simulation_results.shape[0] * num_simulations}")
    print(f"Simulations per Second: {(simulation_results.shape[0] * num_simulations) / execution_time:.2f}")
    
    # 8. Save Results
    print("\n8. Saving Results...")
    
    # Save simulation results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_filename = f"simulation_results_{timestamp}.csv"
    simulation_results.to_csv(results_filename)
    print(f"Results saved to {results_filename}")

    # Save performance metrics
    performance = {
        'execution_time': execution_time,
        'num_portfolios': simulation_results.shape[0],
        'simulations_per_portfolio': num_simulations,
        'total_simulations': simulation_results.shape[0] * num_simulations,
        'simulations_per_second': (simulation_results.shape[0] * num_simulations) / execution_time,
        'best_sharpe': best_sharpe,
        'best_return': best_return,
        'best_volatility': best_volatility
    }

    # Save performance metrics to CSV
    metrics_filename = f"performance_metrics_{timestamp}.csv"
    pd.DataFrame([performance]).to_csv(metrics_filename, index=False)
    print(f"Performance metrics saved to {metrics_filename}")

    print("\nPerformance Metrics:")
    for key, value in performance.items():
        print(f"{key}: {value}")
    
    print("\nOptifolio demonstration completed successfully!")

if __name__ == "__main__":
    main()
