import random
from datetime import datetime

class DataService:
    def __init__(self, use_real_data=False):
        self.use_real_data = use_real_data

    def get_real_time_price(self, symbol):
        """Simule la récupération de prix en temps réel"""
        base_prices = {
            'AAPL': 150 + random.uniform(-5, 5),
            'MSFT': 300 + random.uniform(-10, 10),
            '^TNX': 100 + random.uniform(-2, 2),
            'GLD': 180 + random.uniform(-3, 3),
            'VNQ': 80 + random.uniform(-2, 2)
        }
        return base_prices.get(symbol, 100 + random.uniform(-10, 10))

    def get_portfolio_real_time_value(self, portfolio):
        """Met à jour la valeur du portefeuille avec les prix actuels"""
        total_value = 0
        for asset in portfolio.assets:
            asset.update_current_price(self)
            total_value += asset.current_value or 0

        portfolio.total_value = total_value
        return total_value

    def get_historical_data(self, symbol, days=365):
        """Simule les données historiques pour le calcul de risque"""
        base_price = self.get_real_time_price(symbol)
        returns = []

        for _ in range(days):
            daily_return = random.gauss(0, 0.02)
            returns.append(daily_return)

        return returns