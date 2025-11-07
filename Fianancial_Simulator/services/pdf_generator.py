from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_simulation_report(self, simulation_data, output_path):
        """Génère un rapport PDF pour une simulation - CORRIGÉ POUR LE FUSEAU HORAIRE"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            elements = []

            # Titre du rapport
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,
                textColor=colors.HexColor('#1e40af')
            )

            title = Paragraph("RAPPORT DE SIMULATION FINRISK", title_style)
            elements.append(title)

            # Informations de la simulation
            elements.append(self._create_simulation_info(simulation_data))
            elements.append(Spacer(1, 20))

            # Résultats selon le type de simulation
            simulation_type = simulation_data.get('type', '')
            results = simulation_data.get('results', {})

            if simulation_type == 'stress_test':
                elements.extend(self._create_stress_test_results(results))
            elif simulation_type == 'var':
                elements.extend(self._create_var_results(results))
            elif simulation_type == 'solvency_ii':
                elements.extend(self._create_solvency_results(results))

            # Pied de page - CORRECTION: Utiliser datetime.now() pour le nom de fichier
            elements.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )

            # CORRECTION: Obtenir l'heure locale correcte
            from datetime import datetime
            current_time = datetime.now()
            footer = Paragraph(
                f"Généré le {current_time.strftime('%d/%m/%Y à %H:%M:%S')} - FinRisk Simulator",
                footer_style
            )
            elements.append(footer)

            # Génération du PDF
            doc.build(elements)
            return True

        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            return False

    def _create_simulation_info(self, simulation_data):
        """Crée la section d'informations de la simulation"""
        # CORRECTION: Gestion correcte de la date
        created_at = simulation_data.get('created_at', '')
        try:
            if 'T' in created_at:
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d/%m/%Y %H:%M:%S')
            else:
                formatted_date = 'Date non disponible'
        except:
            formatted_date = 'Date non disponible'

        info_data = [
            ['Nom de la simulation:', simulation_data.get('name', 'N/A')],
            ['Type:', self._format_simulation_type(simulation_data.get('type', ''))],
            ['Date de création:', formatted_date],
        ]

        table = Table(info_data, colWidths=[2 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        return table

    def _create_stress_test_results(self, results):
        """Crée la section des résultats de stress test"""
        elements = []

        # Titre section
        section_title = Paragraph("RÉSULTATS DU TEST DE STRESS", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 12))

        # Métriques principales
        portfolio_value = results.get('total_loss', 0) + results.get('remaining_value', 0)
        metrics_data = [
            ['Valeur initiale estimée:', f"€{portfolio_value:,.2f}"],
            ['Perte totale:', f"€{results.get('total_loss', 0):,.2f}"],
            ['Valeur après stress:', f"€{results.get('remaining_value', 0):,.2f}"],
            ['Impact:', f"{results.get('loss_percentage', 0)}%"],
            ['Scénario:', results.get('scenario_name', 'N/A')]
        ]

        metrics_table = Table(metrics_data, colWidths=[2 * inch, 2 * inch])
        metrics_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(metrics_table)

        return elements

    def _create_var_results(self, results):
        """Crée la section des résultats VaR"""
        elements = []

        section_title = Paragraph("RÉSULTATS VALUE AT RISK (VaR)", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 12))

        var_data = [
            ['VaR 95% (1 jour):', f"€{results.get('var_95', 0):,.2f}"],
            ['VaR 99% (1 jour):', f"€{results.get('var_99', 0):,.2f}"],
            ['Expected Shortfall:', f"€{results.get('expected_shortfall', 0):,.2f}"],
            ['Niveau de confiance:', f"{results.get('confidence_level', 0.95) * 100}%"],
            ['Horizon temporel:', f"{results.get('time_horizon', 1)} jour(s)"],
            ['Méthode:', results.get('method', 'Historique')]
        ]

        var_table = Table(var_data, colWidths=[2 * inch, 2 * inch])
        var_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(var_table)

        return elements

    def _create_solvency_results(self, results):
        """Crée la section des résultats Solvabilité II"""
        elements = []

        section_title = Paragraph("RÉSULTATS SOLVABILITÉ II", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 12))

        # Métriques principales
        coverage_ratio = results.get('coverage_ratio', 0)
        status = 'SOLVABLE' if coverage_ratio >= 100 else 'SOUS-CAPITALISÉ'
        status_color = colors.green if coverage_ratio >= 100 else colors.red

        solvency_data = [
            ['Capital Requis (SCR):', f"€{results.get('scr', 0):,.2f}"],
            ['Capital Minimum (MCR):', f"€{results.get('mcr', 0):,.2f}"],
            ['Ratio de Couverture:', f"{coverage_ratio}%"],
            ['Statut:', status]
        ]

        solvency_table = Table(solvency_data, colWidths=[2 * inch, 2 * inch])
        solvency_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (-1, -1), (-1, -1), status_color),
        ]))
        elements.append(solvency_table)

        # Décomposition des risques
        elements.append(Spacer(1, 15))
        risk_title = Paragraph("DÉCOMPOSITION DES RISQUES", self.styles['Heading3'])
        elements.append(risk_title)
        elements.append(Spacer(1, 8))

        risk_data = [
            ['Type de Risque', 'Montant'],
            ['Risque de Marché', f"€{results.get('market_risk', 0):,.2f}"],
            ['Risque de Souscription', f"€{results.get('underwriting_risk', 0):,.2f}"],
            ['Risque de Contrepartie', f"€{results.get('counterparty_risk', 0):,.2f}"]
        ]

        risk_table = Table(risk_data, colWidths=[2.5 * inch, 1.5 * inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(risk_table)

        return elements

    def _format_simulation_type(self, sim_type):
        """Formate le type de simulation pour l'affichage"""
        types = {
            'var': 'Value at Risk (VaR)',
            'stress_test': 'Test de Stress',
            'solvency_ii': 'Solvabilité II'
        }
        return types.get(sim_type, sim_type)