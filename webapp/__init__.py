"""
Fragrantica Web Application.
Application Flask pour visualiser les données de parfums.
"""
from .app import create_app, app

__version__ = '1.0.0'
__all__ = ['create_app', 'app']