import re
import hashlib


class SecurityUtils:

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password_strength(password):
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"

        if not re.search(r'[A-Z]', password):
            return False, "Le mot de passe doit contenir au moins une majuscule"

        if not re.search(r'[a-z]', password):
            return False, "Le mot de passe doit contenir au moins une minuscule"

        if not re.search(r'[0-9]', password):
            return False, "Le mot de passe doit contenir au moins un chiffre"

        return True, "Mot de passe valide"

    @staticmethod
    def generate_api_key():
        import secrets
        return secrets.token_hex(32)

    @staticmethod
    def sanitize_input(input_str):
        if not input_str:
            return ""

        # Échapper les caractères dangereux
        sanitized = re.sub(r'[<>&"\';]', '', str(input_str))
        return sanitized.strip()