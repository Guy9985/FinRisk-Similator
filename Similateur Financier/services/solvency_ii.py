import numpy as np


class SolvencyIICalculator:
    CORRELATION_MATRIX = {
        'market_credit': 0.25,
        'market_life': 0.25,
        'market_non_life': 0.25,
        'credit_life': 0.5,
        'credit_non_life': 0.5,
        'life_non_life': 0.25
    }

    @staticmethod
    def calculate_scr(portfolio_data, parameters=None):
        parameters = parameters or {}

        market_risk_scr = SolvencyIICalculator._calculate_market_risk_scr(portfolio_data)
        credit_risk_scr = SolvencyIICalculator._calculate_credit_risk_scr(portfolio_data)
        life_risk_scr = SolvencyIICalculator._calculate_life_risk_scr(portfolio_data)
        non_life_risk_scr = SolvencyIICalculator._calculate_non_life_risk_scr(portfolio_data)

        total_scr = SolvencyIICalculator._calculate_total_scr(
            market_risk_scr, credit_risk_scr, life_risk_scr, non_life_risk_scr
        )

        return {
            'total_scr': total_scr,
            'market_risk_scr': market_risk_scr,
            'credit_risk_scr': credit_risk_scr,
            'life_risk_scr': life_risk_scr,
            'non_life_risk_scr': non_life_risk_scr,
            'scr_coverage': SolvencyIICalculator._calculate_coverage_ratio(portfolio_data, total_scr),
            'minimum_capital_requirement': total_scr * 0.45,
            'solvency_ratio': (sum(asset['value'] for asset in portfolio_data['assets']) / total_scr) * 100
        }

    @staticmethod
    def _calculate_market_risk_scr(portfolio_data):
        equity_risk = sum(asset['value'] for asset in portfolio_data['assets'] if asset.get('type') == 'equity') * 0.39
        interest_risk = sum(asset['value'] for asset in portfolio_data['assets'] if asset.get('type') == 'bond') * 0.1
        property_risk = sum(
            asset['value'] for asset in portfolio_data['assets'] if asset.get('type') == 'real_estate') * 0.25
        return (equity_risk ** 2 + interest_risk ** 2 + property_risk ** 2) ** 0.5

    @staticmethod
    def _calculate_credit_risk_scr(portfolio_data):
        return sum(
            asset['value'] for asset in portfolio_data['assets'] if asset.get('type') in ['bond', 'credit']) * 0.08

    @staticmethod
    def _calculate_life_risk_scr(portfolio_data):
        return sum(asset['value'] for asset in portfolio_data['assets'] if asset.get('type') == 'insurance') * 0.12

    @staticmethod
    def _calculate_non_life_risk_scr(portfolio_data):
        return sum(
            asset['value'] for asset in portfolio_data['assets'] if asset.get('type') == 'non_life_insurance') * 0.15

    @staticmethod
    def _calculate_total_scr(market_risk, credit_risk, life_risk, non_life_risk):
        correlations = SolvencyIICalculator.CORRELATION_MATRIX
        total = market_risk ** 2 + credit_risk ** 2 + life_risk ** 2 + non_life_risk ** 2
        total += 2 * correlations['market_credit'] * market_risk * credit_risk
        total += 2 * correlations['market_life'] * market_risk * life_risk
        total += 2 * correlations['market_non_life'] * market_risk * non_life_risk
        total += 2 * correlations['credit_life'] * credit_risk * life_risk
        total += 2 * correlations['credit_non_life'] * credit_risk * non_life_risk
        total += 2 * correlations['life_non_life'] * life_risk * non_life_risk
        return total ** 0.5

    @staticmethod
    def _calculate_coverage_ratio(portfolio_data, scr):
        own_funds = sum(asset['value'] for asset in portfolio_data['assets']) * 0.85
        return (own_funds / scr) * 100 if scr > 0 else float('inf')

    @staticmethod
    def calculate_own_funds(portfolio_data, liabilities=0):
        assets = sum(asset['value'] for asset in portfolio_data['assets'])
        return max(0, assets - liabilities)