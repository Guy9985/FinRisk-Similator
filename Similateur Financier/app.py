from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from config import Config
from database.models import db, Simulation, Portfolio, Scenario
from services.risk_calculations import RiskCalculator
from services.stress_test import StressTestEngine
from services.solvency_ii import SolvencyIICalculator
from utils.data_processor import DataProcessor
from utils.report_generator import ReportGenerator
from datetime import datetime
import json
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser la base de données
    db.init_app(app)
    CORS(app)

    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()
        # Créer des scénarios par défaut
        StressTestEngine._create_default_scenarios()

    # Routes principales
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

    # Gestion des simulations
    @app.route('/api/simulations', methods=['GET', 'POST'])
    def manage_simulations():
        if request.method == 'GET':
            try:
                limit = request.args.get('limit', 10, type=int)
                sim_type = request.args.get('type')

                query = Simulation.query
                if sim_type:
                    query = query.filter_by(simulation_type=sim_type)

                simulations = query.order_by(Simulation.created_at.desc()).limit(limit).all()
                return jsonify([sim.to_dict() for sim in simulations])
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif request.method == 'POST':
            try:
                data = request.get_json()
                simulation = Simulation(
                    name=data.get('name', 'Unnamed Simulation'),
                    simulation_type=data.get('type', 'custom'),
                    parameters=json.dumps(data.get('parameters', {})),
                    results=json.dumps({}),
                    status='pending'
                )
                db.session.add(simulation)
                db.session.commit()
                return jsonify(simulation.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # Stress Testing
    @app.route('/api/simulations/stress-test', methods=['POST'])
    def run_stress_test_simulation():
        try:
            data = request.get_json()
            portfolio_data = DataProcessor.process_portfolio_data(data.get('portfolio', {}))
            scenarios = data.get('scenarios', StressTestEngine.DEFAULT_SCENARIOS)

            results = StressTestEngine.run_stress_test(portfolio_data, scenarios)

            simulation = Simulation(
                name=f"Stress Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                simulation_type='stress_test',
                parameters=json.dumps(data),
                results=json.dumps(results),
                status='completed',
                completed_at=datetime.utcnow()
            )

            db.session.add(simulation)
            db.session.commit()

            return jsonify({
                'simulation_id': simulation.id,
                'results': results,
                'visualization': ReportGenerator.generate_visualization(results)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Solvency II
    @app.route('/api/simulations/solvency-ii', methods=['POST'])
    def run_solvency_ii_simulation():
        try:
            data = request.get_json()
            portfolio_data = DataProcessor.process_portfolio_data(data.get('portfolio', {}))

            results = SolvencyIICalculator.calculate_scr(portfolio_data, data.get('parameters', {}))

            simulation = Simulation(
                name=f"Solvency II - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                simulation_type='solvency_ii',
                parameters=json.dumps(data),
                results=json.dumps(results),
                status='completed',
                completed_at=datetime.utcnow()
            )

            db.session.add(simulation)
            db.session.commit()

            return jsonify({
                'simulation_id': simulation.id,
                'results': results
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Market Risk
    @app.route('/api/simulations/market-risk', methods=['POST'])
    def run_market_risk_simulation():
        try:
            data = request.get_json()
            portfolio_data = DataProcessor.process_portfolio_data(data.get('portfolio', {}))
            confidence_level = data.get('confidence_level', 0.95)
            time_horizon = data.get('time_horizon', 1)
            method = data.get('method', 'historical')

            var_result = RiskCalculator.calculate_var(portfolio_data, confidence_level, time_horizon, method)
            es_result = RiskCalculator.calculate_expected_shortfall(portfolio_data, confidence_level, time_horizon)
            greeks = RiskCalculator.calculate_greeks(portfolio_data)

            results = {
                'var': var_result,
                'expected_shortfall': es_result,
                'greeks': greeks,
                'confidence_level': confidence_level,
                'time_horizon': time_horizon,
                'method': method
            }

            simulation = Simulation(
                name=f"Market Risk - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                simulation_type='market_risk',
                parameters=json.dumps(data),
                results=json.dumps(results),
                status='completed',
                completed_at=datetime.utcnow()
            )

            db.session.add(simulation)
            db.session.commit()

            return jsonify({
                'simulation_id': simulation.id,
                'results': results
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Métriques et données
    @app.route('/api/metrics', methods=['GET'])
    def get_current_metrics():
        try:
            recent_simulations = Simulation.query.filter_by(status='completed') \
                .order_by(Simulation.completed_at.desc()).limit(5).all()

            sample_portfolio = DataProcessor.generate_sample_portfolio()
            portfolio_value = sample_portfolio['total_value']

            metrics = {
                'current_var': RiskCalculator.calculate_var(sample_portfolio, 0.95, 1),
                'stress_loss':
                    StressTestEngine.run_stress_test(sample_portfolio, [StressTestEngine.DEFAULT_SCENARIOS[0]])[
                        'max_loss'],
                'scr_coverage': SolvencyIICalculator.calculate_scr(sample_portfolio)['scr_coverage'],
                'portfolio_value': portfolio_value,
                'recent_simulations': [sim.to_dict() for sim in recent_simulations],
                'portfolio_metrics': DataProcessor.calculate_portfolio_metrics(sample_portfolio)
            }

            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Gestion des portfolios
    @app.route('/api/portfolios', methods=['GET', 'POST'])
    def manage_portfolios():
        if request.method == 'GET':
            try:
                # Pour l'instant, retourner un portfolio sample
                sample_portfolio = DataProcessor.generate_sample_portfolio()
                return jsonify([{
                    'id': 1,
                    'name': 'Portfolio Principal',
                    'description': 'Portfolio de démonstration',
                    'assets': sample_portfolio['assets'],
                    'total_value': sample_portfolio['total_value'],
                    'created_at': datetime.now().isoformat()
                }])
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif request.method == 'POST':
            try:
                data = request.get_json()
                portfolio = Portfolio(
                    name=data['name'],
                    description=data.get('description', ''),
                    assets=json.dumps(data['assets']),
                    user_id=1  # Mock user ID
                )
                db.session.add(portfolio)
                db.session.commit()
                return jsonify(portfolio.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # Scénarios
    @app.route('/api/scenarios', methods=['GET'])
    def get_scenarios():
        try:
            scenarios = Scenario.query.filter_by(is_default=True).all()
            scenarios_data = [{
                'id': sc.id,
                'name': sc.name,
                'description': sc.description,
                'parameters': json.loads(sc.parameters)
            } for sc in scenarios]

            # Ajouter les scénarios par défaut
            scenarios_data.extend(StressTestEngine.DEFAULT_SCENARIOS)

            return jsonify(scenarios_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Rapports
    @app.route('/api/reports/<int:simulation_id>', methods=['GET'])
    def get_simulation_report(simulation_id):
        try:
            simulation = Simulation.query.get_or_404(simulation_id)
            report_format = request.args.get('format', 'json')

            report = ReportGenerator.generate_simulation_report(
                simulation.to_dict(), format=report_format
            )

            if report_format == 'html':
                return report
            else:
                return jsonify(json.loads(report))
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Téléchargement
    @app.route('/api/download/<int:simulation_id>', methods=['GET'])
    def download_simulation(simulation_id):
        try:
            simulation = Simulation.query.get_or_404(simulation_id)
            report = ReportGenerator.generate_simulation_report(simulation.to_dict(), 'json')

            # Créer un fichier temporaire
            from tempfile import NamedTemporaryFile
            import json

            temp_file = NamedTemporaryFile(delete=False, suffix='.json')
            with open(temp_file.name, 'w') as f:
                json.dump(json.loads(report), f, indent=2)

            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f"simulation_report_{simulation_id}.json",
                mimetype='application/json'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)