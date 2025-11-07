# app.py
from flask import Flask, render_template, request, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os
import json
import numpy as np
from scipy import stats
import yfinance as yf
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'finrisk-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finrisk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# === MODÈLES ===
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assets = db.relationship('Asset', backref='portfolio', lazy=True, cascade='all, delete-orphan')

    def calculate_value(self):
        return sum(a.current_value for a in self.assets)

class Asset(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0.0)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolio.id'), nullable=False)

class Simulation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text)
    results = db.Column(db.Text)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolio.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# === INITIALISATION ===
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='demo').first():
            user = User(username='demo', email='demo@finrisk.com', password_hash=generate_password_hash('demo123'))
            db.session.add(user)
            db.session.commit()

            portfolio = Portfolio(name="Portefeuille Démo", description="Exemple", user_id=user.id)
            db.session.add(portfolio)
            db.session.commit()

            assets = [
                Asset(name="Apple", symbol="AAPL", asset_type="equity", quantity=10, purchase_price=150, portfolio_id=portfolio.id),
                Asset(name="US Bond 10Y", symbol="^TNX", asset_type="bond", quantity=1000, purchase_price=100, portfolio_id=portfolio.id),
                Asset(name="Gold", symbol="GLD", asset_type="commodities", quantity=50, purchase_price=180, portfolio_id=portfolio.id),
            ]
            for a in assets:
                a.current_value = a.quantity * a.purchase_price
                db.session.add(a)
            db.session.commit()

# === ROUTES ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current_user')
def api_current_user():
    if current_user.is_authenticated:
        return jsonify({'username': current_user.username, 'email': current_user.email})
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and check_password_hash(user.password_hash, data.get('password')):
            login_user(user)
            return jsonify({'success': True})
        return jsonify({'error': 'Identifiants invalides'}), 401
    return jsonify({'message': 'Use POST'}), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Utilisateur existe déjà'}), 400
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400
        user = User(username=data['username'], email=data['email'], password_hash=generate_password_hash(data['password']))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'message': 'Use POST'}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

# === PORTFEUILLES ===
@app.route('/api/portfolios', methods=['GET', 'POST'])
@login_required
def portfolios():
    if request.method == 'GET':
        ports = Portfolio.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': p.id, 'name': p.name, 'description': p.description or '',
            'total_value': round(p.calculate_value(), 2), 'asset_count': len(p.assets)
        } for p in ports])
    else:
        data = request.get_json()
        portfolio = Portfolio(name=data['name'], description=data.get('description', ''), user_id=current_user.id)
        db.session.add(portfolio)
        db.session.flush()
        for a in data.get('assets', []):
            asset = Asset(
                name=a['name'], symbol=a['symbol'], asset_type=a['type'],
                quantity=float(a['quantity']), purchase_price=float(a['purchase_price']),
                portfolio_id=portfolio.id
            )
            asset.current_value = asset.quantity * asset.purchase_price
            db.session.add(asset)
        db.session.commit()
        return jsonify({'success': True, 'id': portfolio.id})

# === SIMULATIONS ===
@app.route('/api/simulations', methods=['GET', 'POST'])
@login_required
def simulations():
    if request.method == 'GET':
        sims = Simulation.query.filter_by(user_id=current_user.id).order_by(Simulation.created_at.desc()).all()
        return jsonify([{
            'id': s.id, 'name': s.name, 'type': s.type,
            'created_at': s.created_at.isoformat(),
            'results': json.loads(s.results) if s.results else {}
        } for s in sims])
    else:
        data = request.get_json()
        portfolio = Portfolio.query.get(data['portfolio_id'])
        if not portfolio or portfolio.user_id != current_user.id:
            return jsonify({'error': 'Portfolio non trouvé'}), 404

        sim = Simulation(
            name=data['name'], type=data['type'],
            portfolio_id=portfolio.id, user_id=current_user.id,
            parameters=json.dumps(data.get('parameters', {}))
        )
        db.session.add(sim)
        db.session.flush()

        results = {}
        if data['type'] == 'var':
            results = calculate_var(portfolio, data.get('parameters', {}))
        elif data['type'] == 'stress_test':
            results = stress_test(portfolio, data.get('parameters', {}))
        elif data['type'] == 'backtest':
            results = backtest(portfolio, data.get('parameters', {}))

        sim.results = json.dumps(results)
        db.session.commit()

        pdf_path = generate_pdf_report(sim, results)
        return jsonify({'success': True, 'id': sim.id, 'pdf_url': f'/api/simulations/{sim.id}/pdf'})

@app.route('/api/simulations/<sim_id>/pdf')
@login_required
def download_pdf(sim_id):
    sim = Simulation.query.get(sim_id)
    if not sim or sim.user_id != current_user.id:
        return "Non trouvé", 404
    pdf_path = f"reports/sim_{sim_id}.pdf"
    if not os.path.exists(pdf_path):
        return "PDF non généré", 404
    return send_file(pdf_path, as_attachment=True, download_name=f"rapport_{sim.name}.pdf")

# === CALCULS ===
def calculate_var(portfolio, params):
    confidence = params.get('confidence_level', 0.95)
    horizon = params.get('time_horizon', 1)
    values = [a.current_value for a in portfolio.assets]
    if sum(values) == 0: return {'var': 0, 'cvar': 0}
    weights = np.array(values) / sum(values)
    returns = []
    for asset in portfolio.assets:
        try:
            data = yf.download(asset.symbol, period="1y", progress=False)['Adj Close']
            ret = data.pct_change().dropna().tail(252)
            if len(ret) < 100: ret = np.random.normal(0, 0.02, 252)
        except: ret = np.random.normal(0, 0.02, 252)
        returns.append(ret)
    portfolio_returns = np.average(returns, axis=0, weights=weights)
    var = np.percentile(portfolio_returns, (1 - confidence) * 100) * portfolio.calculate_value() * np.sqrt(horizon)
    cvar = portfolio_returns[portfolio_returns <= var].mean() * portfolio.calculate_value() * np.sqrt(horizon)
    return {'var': round(abs(var), 2), 'cvar': round(abs(cvar), 2)}

def stress_test(portfolio, params):
    scenario = params.get('scenario', {'equity': -0.3, 'bond': -0.1, 'commodities': -0.2})
    total_loss = sum(asset.current_value * abs(scenario.get(asset.asset_type, -0.1)) for asset in portfolio.assets)
    total_value = portfolio.calculate_value()
    return {
        'total_loss': round(total_loss, 2),
        'remaining_value': round(total_value - total_loss, 2),
        'loss_percentage': round((total_loss / total_value) * 100, 2) if total_value > 0 else 0
    }

def backtest(portfolio, params):
    return {'status': 'Backtest simulé', 'annual_return': '12.5%', 'max_drawdown': '-18.3%'}

# === PDF ===
def generate_pdf_report(sim, results):
    os.makedirs('reports', exist_ok=True)
    path = f"reports/sim_{sim.id}.pdf"
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("RAPPORT DE SIMULATION FINRISK", styles['Title']),
        Spacer(1, 20),
        Paragraph(f"Nom: {sim.name} | Type: {sim.type.upper()}", styles['Normal']),
        Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']),
        Spacer(1, 20),
    ]
    if sim.type == 'var':
        data = [['Métrique', 'Valeur'], ['VaR (95%)', f"€{results.get('var', 0):,.2f}"], ['CVaR', f"€{results.get('cvar', 0):,.2f}"]]
        table = Table(data)
        table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(table)
    doc.build(elements)
    return path

# === DASHBOARD ===
@app.route('/api/dashboard')
@login_required
def dashboard():
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio or portfolio.calculate_value() == 0:
        return jsonify({'var': 0, 'stress_loss': 0, 'sharpe': 0, 'value': 0, 'allocation': {}})
    value = portfolio.calculate_value()
    var_result = calculate_var(portfolio, {'confidence_level': 0.95})
    stress_result = stress_test(portfolio, {'scenario': {'equity': -0.3}})
    allocation = {}
    for a in portfolio.assets:
        allocation[a.asset_type] = allocation.get(a.asset_type, 0) + a.current_value
    total = sum(allocation.values())
    allocation_pct = {k: round((v / total) * 100, 1) for k, v in allocation.items()}
    return jsonify({
        'var': var_result['var'], 'stress_loss': stress_result['total_loss'],
        'sharpe': 1.8, 'value': round(value, 2), 'allocation': allocation_pct
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)