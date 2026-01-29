#!/usr/bin/env python3
"""Test le chargement des URLs depuis MongoDB."""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def test_url_loading():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    mongo_db = os.getenv('MONGO_DATABASE', 'fragrantica')
    
    print(f"Connexion à: {mongo_uri}")
    print(f"Base de données: {mongo_db}")
    print()
    
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[mongo_db]
    
    # Test 1: Compter tous les documents
    total = db.perfume_urls.count_documents({})
    print(f"Total URLs en base: {total}")
    
    # Test 2: Compter par designer
    designers_count = db.perfume_urls.aggregate([
        {"$group": {"_id": "$designer", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    
    print("\nTop 10 designers par nombre d'URLs:")
    for doc in designers_count:
        print(f"  {doc['_id']}: {doc['count']} URLs")
    
    # Test 3: Charger toutes les URLs en mémoire (comme le spider)
    print("\nChargement de toutes les URLs en mémoire...")
    existing_urls = set()
    cursor = db.perfume_urls.find({}, {"perfume_url": 1, "_id": 0})
    
    for doc in cursor:
        if "perfume_url" in doc:
            existing_urls.add(doc["perfume_url"])
    
    print(f"URLs chargées en mémoire: {len(existing_urls)}")
    
    if len(existing_urls) != total:
        print(f"⚠️  ERREUR: {total} docs en base mais seulement {len(existing_urls)} URLs chargées!")
    else:
        print("✅ Chargement OK - tous les documents ont été chargés")
    
    # Test 4: Vérifier quelques URLs spécifiques de d'Annam
    dannam_urls = list(db.perfume_urls.find(
        {"designer": "d'Annam"},
        {"perfume_url": 1, "_id": 0}
    ).limit(5))
    
    print("\nExemple d'URLs de d'Annam en base:")
    for url_doc in dannam_urls:
        url = url_doc["perfume_url"]
        in_set = url in existing_urls
        print(f"  {url}")
        print(f"    -> Dans le set? {in_set}")
    
    client.close()

if __name__ == "__main__":
    test_url_loading()