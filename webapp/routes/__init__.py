"""
Routes de l'application Flask.
"""
from .main import main_bp
from .perfumes import perfumes_bp
from .api import api_bp

__all__ = ['main_bp', 'perfumes_bp', 'api_bp']