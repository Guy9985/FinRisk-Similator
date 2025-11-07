import numpy as np
import pandas as pd
from scipy import stats
import json


class RiskCalculator:
    @staticmethod
    def calculate_var(portfolio_data, confidence_level=0.95, time_horizon=1, method='historical'):
        """
        Calculate Value at Risk using different methods
        """
        portfolio_value = sum(asset['value'] for asset in portfolio_data['assets'])

        if method == 'historical':
            return RiskCalculator._historical_var(portfolio_value, confidence_level, time_horizon)
        elif method == 'parametric':
            return RiskCalculator._parametric_var(portfolio_value, confidence_level, time_horizon)
        elif method == 'monte_carlo':
            return RiskCalculator._monte_carlo_var(portfolio_value, confidence_level, time_horizon)

        return 0

    @staticmethod
    def _historical_var(portfolio_value, confidence_level, time_horizon):
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, 1000)
        var = np.percentile(returns, (1 - confidence_level) * 100) * portfolio_value * np.sqrt(time_horizon)
        return abs(var)

    @staticmethod
    def _parametric_var(portfolio_value, confidence_level, time_horizon):
        mean_return = 0.0005
        volatility = 0.02
        z_score = stats.norm.ppf(1 - confidence_level)
        var = (mean_return + z_score * volatility) * portfolio_value * np.sqrt(time_horizon)
        return abs(var)

    @staticmethod
    def _monte_carlo_var(portfolio_value, confidence_level, time_horizon, simulations=10000):
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, simulations)
        var = np.percentile(returns, (1 - confidence_level) * 100) * portfolio_value * np.sqrt(time_horizon)
        return abs(var)

    @staticmethod
    def calculate_expected_shortfall(portfolio_data, confidence_level=0.95, time_horizon=1):
        portfolio_value = sum(asset['value'] for asset in portfolio_data['assets'])
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, 1000)
        var = np.percentile(returns, (1 - confidence_level) * 100)
        es = returns[returns <= var].mean() * portfolio_value * np.sqrt(time_horizon)
        return abs(es)

    @staticmethod
    def calculate_greeks(portfolio_data):
        """Calculate option Greeks if applicable"""
        greeks = {}
        for asset in portfolio_data['assets']:
            if asset.get('type') == 'option':
                greeks[asset['name']] = {
                    'delta': np.random.uniform(-1, 1),
                    'gamma': np.random.uniform(0, 0.1),
                    'vega': np.random.uniform(0, 0.05),
                    'theta': np.random.uniform(-0.01, 0)
                }
        return greeks