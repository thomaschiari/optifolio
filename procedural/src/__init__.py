"""
Optifolio - A portfolio optimization library.

This package provides tools for loading stock data, simulating portfolios,
and visualizing the results.
"""

from .data_loader import DataLoader
from .simulate import PortfolioSimulator
from .utils import PortfolioMetrics
from .data_viz import DataViz

__all__ = [
    'DataLoader',
    'PortfolioSimulator',
    'PortfolioMetrics',
    'DataViz'
]
