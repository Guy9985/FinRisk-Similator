#!/usr/bin/env python3
"""
Script d'installation et d'initialisation de FinRisk Simulator
"""
import os
import sys
from database.models import db, Scenario
from services.stress_test import StressTestEngine
from app import create_app


def setup_application():
    app = create_app()

    with app.app_context():
        # Créer les tables
        db.create_all()

        # Créer les scénarios par défaut
        for scenario_data in StressTestEngine.DEFAULT_SCENARIOS:
            scenario = Scenario(
                name=scenario_data['name'],
                description=scenario_data['description'],
                parameters=json.dumps(scenario_data['shocks']),
                is_default=True
            )
            db.session.add(scenario)

        db.session.commit()
        print("✅ Application initialisée avec succès!")
        print("📊 Scénarios par défaut créés")


if __name__ == '__main__':
    setup_application()