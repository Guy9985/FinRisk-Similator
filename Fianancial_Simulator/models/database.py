from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    simulations = db.relationship('Simulation', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_value = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assets = db.relationship('Asset', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', backref='portfolio', lazy=True)

    def calculate_total_value(self):
        self.total_value = sum(asset.current_value for asset in self.assets if asset.current_value)
        return self.total_value

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'total_value': self.total_value,
            'created_at': self.created_at.isoformat(),
            'assets': [asset.to_dict() for asset in self.assets]
        }

class Asset(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20))
    asset_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    def update_current_price(self, data_service):
        try:
            if self.symbol:
                price = data_service.get_real_time_price(self.symbol)
                if price:
                    self.current_value = self.quantity * price
                    return
            self.current_value = self.quantity * self.purchase_price
        except Exception:
            self.current_value = self.quantity * self.purchase_price

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'type': self.asset_type,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'current_value': self.current_value
        }

class Simulation(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    simulation_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text)
    results = db.Column(db.Text)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_parameters(self, params):
        self.parameters = json.dumps(params)

    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}

    def set_results(self, results):
        self.results = json.dumps(results)

    def get_results(self):
        return json.loads(self.results) if self.results else {}

class Scenario(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_parameters(self, params):
        self.parameters = json.dumps(params)

    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}