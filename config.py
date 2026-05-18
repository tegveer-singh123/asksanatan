"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "asksanatan-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///asksanatan.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Admin credentials from environment
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Admin")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@asksanatan.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@12345")

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
