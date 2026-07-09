"""Application configuration — mirrors application.yml."""
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///booking_v3.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Server port (used by run.py — Flask defaults to 5000, Java used 9090)
    SERVER_PORT = int(os.environ.get('SERVER_PORT', 9090))
