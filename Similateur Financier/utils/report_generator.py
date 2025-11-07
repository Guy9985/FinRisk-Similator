import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64


class ReportGenerator:
    @staticmethod
    def generate_simulation_report(simulation_data, format='json'):
        """Generate comprehensive simulation report"""
        report = {
            'metadata': {
                'report_id': f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'simulation_type': simulation_data.get('type', 'unknown'),
                'simulation_id': simulation_data.get('id')
            },
            'executive_summary': ReportGenerator._generate_executive_summary(simulation_data),
            'detailed_results': simulation_data.get('results', {}),
            'risk_metrics': ReportGenerator._calculate_risk_metrics(simulation_data),
            'recommendations': ReportGenerator._generate_recommendations(simulation_data)
        }

        if format == 'json':
            return json.dumps(report, indent=2)
        elif format == 'html':
            return ReportGenerator._generate_html_report(report)

        return report

    @staticmethod
    def _generate_executive_summary(simulation_data):
        results = simulation_data.get('results', {})
        return {
            'total_impact': results.get('max_loss', 0),
            'key_findings': [
                f"Maximum loss scenario: {results.get('most_severe_scenario', 'Unknown')}",
                f"Portfolio value: €{results.get('portfolio_value', 0):,.2f}",
                f"Maximum potential loss: €{results.get('max_loss', 0):,.2f}"
            ],
            'risk_level': ReportGenerator._assess_risk_level(results.get('max_loss', 0),
                                                             results.get('portfolio_value', 1))
        }

    @staticmethod
    def _calculate_risk_metrics(simulation_data):
        results = simulation_data.get('results', {})
        portfolio_value = results.get('portfolio_value', 1)
        max_loss = results.get('max_loss', 0)

        return {
            'loss_ratio': (max_loss / portfolio_value) * 100,
            'risk_adjusted_return': 0.08,  # Mock value
            'value_at_risk': max_loss * 0.7,  # Mock value
            'expected_shortfall': max_loss * 0.8  # Mock value
        }

    @staticmethod
    def _generate_recommendations(simulation_data):
        results = simulation_data.get('results', {})
        loss_ratio = (results.get('max_loss', 0) / results.get('portfolio_value', 1)) * 100

        recommendations = []
        if loss_ratio > 30:
            recommendations.append("Consider significant portfolio diversification")
            recommendations.append("Increase hedging strategies")
            recommendations.append("Review risk management policies")
        elif loss_ratio > 20:
            recommendations.append("Moderate portfolio rebalancing recommended")
            recommendations.append("Consider additional hedging")
        else:
            recommendations.append("Portfolio risk level acceptable")
            recommendations.append("Continue current risk management strategy")

        return recommendations

    @staticmethod
    def _assess_risk_level(max_loss, portfolio_value):
        loss_ratio = (max_loss / portfolio_value) * 100
        if loss_ratio > 30:
            return "HIGH"
        elif loss_ratio > 20:
            return "MEDIUM-HIGH"
        elif loss_ratio > 10:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _generate_html_report(report_data):
        # Simplified HTML report generation
        html = f"""
        <html>
        <head>
            <title>Risk Simulation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .risk-high {{ color: red; font-weight: bold; }}
                .risk-medium {{ color: orange; }}
                .risk-low {{ color: green; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Financial Risk Simulation Report</h1>
                <p>Generated: {report_data['metadata']['generated_at']}</p>
            </div>

            <div class="section">
                <h2>Executive Summary</h2>
                <p>Risk Level: <span class="risk-{report_data['executive_summary']['risk_level'].lower()}">
                    {report_data['executive_summary']['risk_level']}
                </span></p>
                <ul>
                    {''.join(f'<li>{finding}</li>' for finding in report_data['executive_summary']['key_findings'])}
                </ul>
            </div>

            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report_data['recommendations'])}
                </ul>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def generate_visualization(data, chart_type='bar'):
        """Generate visualization for simulation results"""
        plt.figure(figsize=(10, 6))

        if chart_type == 'bar':
            labels = [result['scenario_name'] for result in data.get('scenario_results', [])]
            values = [result['total_loss'] for result in data.get('scenario_results', [])]
            plt.bar(labels, values)
            plt.title('Stress Test Results by Scenario')
            plt.xticks(rotation=45)
            plt.ylabel('Loss (EUR)')

        plt.tight_layout()

        # Convert to base64 for HTML embedding
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')