#!/usr/bin/env python3
"""Script de test de la connexion MongoDB"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Charger .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_connection():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    mongo_db = os.getenv('MONGO_DATABASE', 'fragrantica')
    
    print(f"🔍 Test de connexion à MongoDB")
    print(f"   URI: {mongo_uri}")
    print(f"   Database: {mongo_db}")
    print()
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion MongoDB réussie !")
        
        # Afficher les bases de données
        dbs = client.list_database_names()
        print(f"📊 Bases de données disponibles: {', '.join(dbs)}")
        
        # Vérifier les collections
        db = client[mongo_db]
        collections = db.list_collection_names()
        
        if collections:
            print(f"📚 Collections dans '{mongo_db}': {', '.join(collections)}")
            
            # Compter les documents
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"   - {coll}: {count:,} documents")
        else:
            print(f"ℹ️  La base '{mongo_db}' est vide (normal au premier lancement)")
        
        client.close()
        print("\n✅ Test terminé avec succès !")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n💡 Vérifiez que MongoDB est démarré:")
        print("   docker-compose up -d")
        return False
    
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_connection()