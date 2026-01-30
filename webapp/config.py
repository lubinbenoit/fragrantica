"""
Configuration de l'application Flask.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # MongoDB
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb://admin:password123@mongodb:27017/'
    )
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'fragrantica')
    
    # Collections
    COLLECTION_URLS = 'perfume_urls'
    COLLECTION_DATA = 'perfume_data'
    
    # Pagination
    ITEMS_PER_PAGE = 24
    
    # Cache (optionnel)
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Configuration développement."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration production."""
    DEBUG = False
    # En production, forcer l'utilisation de variables d'environnement
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")


# Sélection de la config selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retourne la configuration selon l'environnement."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])