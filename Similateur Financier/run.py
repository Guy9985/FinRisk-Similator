#!/usr/bin/env python3
"""
Script de lancement de l'application FinRisk Simulator
"""
import os
import sys
from app import create_app


def main():
    # Créer le répertoire uploads s'il n'existe pas
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('database', exist_ok=True)

    app = create_app()

    print("🚀 Démarrage de FinRisk Simulator...")
    print("📍 URL: http://localhost:5000")
    print("📊 API: http://localhost:5000/api/health")
    print("💾 Base de données: database/database.db")

    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()