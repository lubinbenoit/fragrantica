"""
Utilitaire de connexion MongoDB pour l'application Flask.
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from flask import current_app, g
import sys


def get_db():
    """
    Récupère la connexion MongoDB.
    Utilise Flask's application context (g) pour réutiliser la connexion.
    """
    if 'db' not in g:
        try:
            client = MongoClient(
                current_app.config['MONGO_URI'],
                serverSelectionTimeoutMS=5000
            )
            # Test de connexion
            client.admin.command('ping')
            g.db = client[current_app.config['MONGO_DATABASE']]
            g.client = client
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            current_app.logger.error(f"MongoDB connection failed: {e}")
            print(f"❌ MongoDB connection failed: {e}")
            print("\n💡 Make sure MongoDB is running:")
            print("   docker-compose up -d mongodb")
            sys.exit(1)
    
    return g.db


def close_db(e=None):
    """
    Ferme la connexion MongoDB à la fin de la requête.
    """
    client = g.pop('client', None)
    if client is not None:
        client.close()


def init_db(app):
    """
    Initialise la connexion MongoDB avec l'application Flask.
    """
    app.teardown_appcontext(close_db)
    
    # Test de connexion au démarrage
    with app.app_context():
        try:
            db = get_db()
            app.logger.info(f"✓ Connected to MongoDB: {app.config['MONGO_DATABASE']}")
            
            # Afficher les collections disponibles
            collections = db.list_collection_names()
            app.logger.info(f"✓ Available collections: {', '.join(collections)}")
            
        except Exception as e:
            app.logger.error(f"✗ MongoDB initialization failed: {e}")
            raise