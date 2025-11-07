import numpy as np
import json
from datetime import datetime, timedelta


class StressTestEngine:
    DEFAULT_SCENARIOS = [
        {
            'id': 1,
            'name': 'Market Crash 2008',
            'description': 'Global financial crisis scenario',
            'shocks': {
                'equity': -0.4,
                'bond': -0.15,
                'real_estate': -0.3,
                'commodities': -0.25,
                'currency': 0.1
            }
        },
        {
            'id': 2,
            'name': 'Interest Rate Shock',
            'description': 'Rapid interest rate increase',
            'shocks': {
                'equity': -0.2,
                'bond': -0.25,
                'real_estate': -0.15,
                'commodities': -0.1,
                'currency': 0.05
            }
        },
        {
            'id': 3,
            'name': 'Liquidity Crisis',
            'description': 'Market liquidity drought',
            'shocks': {
                'equity': -0.3,
                'bond': -0.1,
                'real_estate': -0.4,
                'commodities': -0.2,
                'currency': 0.15
            }
        }
    ]

    @staticmethod
    def run_stress_test(portfolio_data, scenarios, correlation_matrix=None):
        results = []
        portfolio_value = sum(asset['value'] for asset in portfolio_data['assets'])

        for scenario in scenarios:
            scenario_result = StressTestEngine._calculate_scenario_impact(
                portfolio_data, scenario, portfolio_value, correlation_matrix
            )
            results.append(scenario_result)

        return {
            'portfolio_value': portfolio_value,
            'scenario_results': results,
            'max_loss': max(result['total_loss'] for result in results),
            'most_severe_scenario': max(results, key=lambda x: x['total_loss'])['scenario_name'],
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def _calculate_scenario_impact(portfolio_data, scenario, portfolio_value, correlation_matrix):
        total_loss = 0
        asset_impacts = []

        for asset in portfolio_data['assets']:
            asset_type = asset.get('type', 'equity')
            shock = scenario['shocks'].get(asset_type, 0.1)
            loss = asset['value'] * shock

            asset_impacts.append({
                'asset_name': asset['name'],
                'asset_type': asset_type,
                'initial_value': asset['value'],
                'shock_applied': shock,
                'loss': loss,
                'remaining_value': asset['value'] - loss
            })

            total_loss += loss

        # Apply correlation effects if matrix provided
        correlation_impact = StressTestEngine._calculate_correlation_impact(
            asset_impacts, correlation_matrix
        )
        total_loss *= (1 + correlation_impact)

        return {
            'scenario_name': scenario['name'],
            'scenario_id': scenario['id'],
            'total_loss': total_loss,
            'loss_percentage': (total_loss / portfolio_value) * 100,
            'remaining_value': portfolio_value - total_loss,
            'asset_impacts': asset_impacts,
            'correlation_impact': correlation_impact,
            'recovery_estimate': StressTestEngine._estimate_recovery_time(total_loss, portfolio_value)
        }

    @staticmethod
    def _calculate_correlation_impact(asset_impacts, correlation_matrix):
        if not correlation_matrix:
            return np.random.uniform(0.1, 0.3)
        return 0.2  # Simplified

    @staticmethod
    def _estimate_recovery_time(total_loss, portfolio_value):
        loss_ratio = total_loss / portfolio_value
        if loss_ratio > 0.3:
            return 180  # days
        elif loss_ratio > 0.2:
            return 120
        elif loss_ratio > 0.1:
            return 90
        else:
            return 30

    @staticmethod
    def generate_custom_scenario(parameters):
        """Generate custom stress scenario based on parameters"""
        return {
            'name': parameters.get('name', 'Custom Scenario'),
            'shocks': parameters.get('shocks', {})
        }

    @staticmethod
    def _create_default_scenarios():
        """Create default scenarios in the database"""
        # Cette méthode devrait être appelée dans app.py pour initialiser les scénarios
        pass