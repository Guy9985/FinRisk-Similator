import re


class FinancialValidator:
    @staticmethod
    def validate_portfolio_data(data):
        """Valide les données de portefeuille"""
        errors = []

        if not data.get('name') or not data['name'].strip():
            errors.append("Le nom du portefeuille est requis")

        if not data.get('assets') or not isinstance(data['assets'], list):
            errors.append("Au moins un actif est requis")
        else:
            for i, asset in enumerate(data['assets']):
                if not asset.get('name') or not asset['name'].strip():
                    errors.append(f"L'actif {i + 1} doit avoir un nom")

                if not asset.get('quantity') or float(asset.get('quantity', 0)) <= 0:
                    errors.append(f"L'actif {i + 1} doit avoir une quantité valide")

                if not asset.get('purchase_price') or float(asset.get('purchase_price', 0)) < 0:
                    errors.append(f"L'actif {i + 1} doit avoir un prix d'achat valide")

        return errors

    @staticmethod
    def validate_simulation_parameters(data):
        """Valide les paramètres de simulation"""
        errors = []

        if not data.get('name') or not data['name'].strip():
            errors.append("Le nom de la simulation est requis")

        if not data.get('portfolio_id'):
            errors.append("Un portefeuille doit être sélectionné")

        if not data.get('type'):
            errors.append("Le type de simulation est requis")

        simulation_type = data.get('type')
        parameters = data.get('parameters', {})

        if simulation_type == 'stress_test' and not parameters.get('scenario_id'):
            errors.append("Un scénario de stress doit être sélectionné")

        return errors

    @staticmethod
    def sanitize_string(text):
        """Nettoie une chaîne de caractères"""
        if not text:
            return ""
        return re.sub(r'[<>]', '', text.strip())

    @staticmethod
    def validate_financial_value(value, field_name):
        """Valide une valeur financière"""
        try:
            num_value = float(value)
            if num_value < 0:
                raise ValueError(f"{field_name} ne peut pas être négatif")
            return num_value
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} doit être un nombre valide")