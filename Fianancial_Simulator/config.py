class Config:
    SECRET_KEY = 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///finrisk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False