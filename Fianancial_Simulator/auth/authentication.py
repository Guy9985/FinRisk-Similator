from flask_login import LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db, User
import uuid

login_manager = LoginManager()

class AuthService:
    @staticmethod
    def create_user(username, email, password):
        if User.query.filter_by(username=username).first():
            raise ValueError("Nom d'utilisateur déjà utilisé")

        if User.query.filter_by(email=email).first():
            raise ValueError("Email déjà utilisé")

        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def logout_user():
        logout_user()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)