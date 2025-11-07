import pandas as pd
import numpy as np
import json
from datetime import datetime


class DataProcessor:
    @staticmethod
    def process_portfolio_data(raw_data):
        """Process raw portfolio data into standardized format"""
        if isinstance(raw_data, str):
            try:
                data = json.loads(raw_data)
            except:
                data = raw_data
        else:
            data = raw_data

        processed = {
            'assets': [],
            'total_value': 0,
            'currency': 'EUR',
            'as_of_date': datetime.now().isoformat()
        }

        for asset in data.get('assets', []):
            processed_asset = {
                'name': asset.get('name', 'Unnamed Asset'),
                'type': asset.get('type', 'equity'),
                'value': float(asset.get('value', 0)),
                'currency': asset.get('currency', 'EUR'),
                'risk_weight': asset.get('risk_weight', 1.0),
                'liquidity': asset.get('liquidity', 'medium')
            }
            processed['assets'].append(processed_asset)
            processed['total_value'] += processed_asset['value']

        return processed

    @staticmethod
    def generate_sample_portfolio():
        """Generate sample portfolio data for demonstration"""
        return {
            'assets': [
                {'name': 'Apple Inc.', 'type': 'equity', 'value': 25000000, 'currency': 'USD'},
                {'name': 'Microsoft Corp.', 'type': 'equity', 'value': 22000000, 'currency': 'USD'},
                {'name': 'US Treasury Bonds', 'type': 'bond', 'value': 40000000, 'currency': 'USD'},
                {'name': 'Commercial Real Estate', 'type': 'real_estate', 'value': 35000000, 'currency': 'EUR'},
                {'name': 'Gold ETF', 'type': 'commodities', 'value': 15000000, 'currency': 'USD'},
                {'name': 'Corporate Bonds', 'type': 'credit', 'value': 19700000, 'currency': 'EUR'}
            ],
            'total_value': 156700000,
            'currency': 'USD',
            'as_of_date': datetime.now().isoformat()
        }

    @staticmethod
    def calculate_portfolio_metrics(portfolio_data):
        """Calculate various portfolio metrics"""
        metrics = {
            'total_value': sum(asset['value'] for asset in portfolio_data['assets']),
            'asset_allocation': {},
            'currency_exposure': {},
            'risk_concentration': {}
        }

        for asset in portfolio_data['assets']:
            # Asset allocation by type
            asset_type = asset['type']
            metrics['asset_allocation'][asset_type] = metrics['asset_allocation'].get(asset_type, 0) + asset['value']

            # Currency exposure
            currency = asset['currency']
            metrics['currency_exposure'][currency] = metrics['currency_exposure'].get(currency, 0) + asset['value']

            # Risk concentration
            metrics['risk_concentration'][asset['name']] = asset['value']

        return metrics

    @staticmethod
    def convert_currency(value, from_currency, to_currency='EUR'):
        """Simple currency conversion (mock implementation)"""
        conversion_rates = {
            'USD': 0.85,
            'EUR': 1.0,
            'GBP': 1.12,
            'JPY': 0.0076
        }
        return value * conversion_rates.get(from_currency, 1.0) / conversion_rates.get(to_currency, 1.0)