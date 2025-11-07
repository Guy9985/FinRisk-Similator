# FinRisk: Calculateur Actuariel Embarqué

## 🎯 Objectif du Projet

**FinRisk** est une application web de simulation actuarielle développée dans le cadre du Sujet 9 de l'examen de Génie Logiciel. Son objectif principal est de fournir aux professionnels de l'assurance un outil rapide et précis pour le calcul des primes dans trois branches principales : l'Assurance Vie, l'Assurance Non-Vie et l'Assurance Obligatoire.

L'application est conçue pour être un calculateur embarqué, offrant une interface utilisateur intuitive, un moteur de calcul basé sur des modèles actuariels rigoureux (incluant la table de mortalité THP-00/02), un système d'authentification sécurisé et une fonctionnalité de traçabilité des calculs avec génération de rapports PDF.

## 🛠️ Technologies Utilisées

| Composant | Technologie | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.x, Flask | Micro-framework web pour la logique métier et les API. |
| **Base de Données** | SQLite, Flask-SQLAlchemy | Base de données légère pour la gestion des utilisateurs et l'historique des calculs. |
| **Authentification** | Flask-Login, Werkzeug | Gestion des sessions utilisateur et hachage sécurisé des mots de passe. |
| **Calculs Actuariels** | Fonctions Python natives | Implémentation des modèles mathématiques (Décès Temporaire, Vie Entière, Rente Viagère, Modèles Multiplicatifs). |
| **Rapports** | ReportLab | Librairie Python pour la génération de rapports de calcul au format PDF. |
| **Frontend** | HTML5, CSS3, JavaScript | Interface utilisateur pour la saisie des paramètres et l'affichage des résultats. |

## 🚀 Installation et Démarrage

Ces instructions vous permettront d'obtenir une copie du projet opérationnelle sur votre machine locale à des fins de développement et de test.

### Prérequis

Assurez-vous d'avoir Python 3.x et `pip` installés sur votre système.

### Étapes d'Installation

1.  **Cloner le dépôt**
    ```bash
    git clone https://github.com/votre-nom-utilisateur/FinRisk.git
    cd FinRisk
    ```

2.  **Créer et activer l'environnement virtuel**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sur Linux/macOS
    # venv\Scripts\activate  # Sur Windows
    ```

3.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialiser la base de données**
    Le code utilise Flask-SQLAlchemy. Vous devez créer les tables de la base de données.
    Créez un fichier temporaire `init_db.py` :
    ```python
    # init_db.py
    from app import db, app
    with app.app_context():
        db.create_all()
    ```
    Puis exécutez :
    ```bash
    python init_db.py
    ```
    *(Note : Le fichier `app.py` doit être présent dans le répertoire racine pour que cela fonctionne.)*

5.  **Lancer l'application**
    ```bash
    python app.py
    ```

L'application sera accessible à l'adresse `http://127.0.0.1:5000`.

## ⚙️ Utilisation

1.  **Enregistrement et Connexion** : Créez un compte utilisateur ou connectez-vous.
2.  **Calcul de Prime** : Accédez à la page de calcul et sélectionnez l'une des trois branches d'assurance.
3.  **Saisie des Paramètres** : Entrez les paramètres spécifiques (capital, âge, durée, facteurs de risque, etc.).
4.  **Résultats** : La prime calculée est affichée en temps réel.
5.  **Historique et Rapports** : Tous les calculs sont sauvegardés. Vous pouvez consulter l'historique et générer un rapport PDF professionnel pour chaque simulation.

## 📝 Structure du Code

Le projet est structuré autour d'un fichier principal monolithique, mais une refactorisation est recommandée pour une meilleure maintenabilité (voir la section **Perspectives**).

```
FinRisk/
├── app.py                 # Application Flask principale (Routes, Logique, Modèles, Calculs)
├── requirements.txt       # Liste des dépendances Python
├── .gitignore             # Fichiers à ignorer par Git
├── init_db.py             # Script d'initialisation de la base de données
├── calculations.db        # Base de données SQLite (ignorée par .gitignore)
├── templates/             # Fichiers HTML (index.html, login.html, etc.)
└── static/                # Fichiers CSS et JavaScript
```

## 💡 Perspectives d'Évolution

*   **Refactorisation** : Séparer le code monolithique de `app.py` en modules distincts (`models.py`, `calculators.py`, `routes.py`).
*   **Tests Unitaires** : Implémenter des tests unitaires pour les fonctions de calcul actuariel afin de garantir l'exactitude mathématique.
*   **Base de Données** : Migrer vers une base de données de production (PostgreSQL ou MySQL).
*   **API REST** : Développer une API REST complète pour permettre l'intégration avec des systèmes tiers.

## 🤝 Contribution

Les contributions sont les bienvenues. Pour toute suggestion ou correction :

1.  Forkez le projet.
2.  Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`).
3.  Commitez vos changements (`git commit -m 'Ajout de nouvelle fonctionnalité'`).
4.  Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`).
5.  Ouvrez une Pull Request.

## 📄 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT) - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.

## 📧 Contact

Guy Oreste NDIKUMASABO - [guyorestendi@gmail.com]
Lien du Projet : [https://github.com/Guy9985/FinRisk](https://github.com/Guy9985/FinRisk)
s
