#!/usr/bin/env python3
"""Script de diagnostic des URLs"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ✅ Utilise la variable d'environnement (mongodb:27017 dans Docker)
mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017/')
print(f"🔗 Connecting to: {mongo_uri}\n")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['fragrantica']
    
    print("=== Diagnostic MongoDB ===\n")
    
    # Total URLs
    total = db.perfume_urls.count_documents({})
    print(f"Total URLs: {total:,}\n")
    
    # URLs pour d'Annam
    dannam_urls = list(db.perfume_urls.find(
        {"designer": "d'Annam"}, 
        {"perfume_url": 1, "_id": 0}
    ))
    print(f"URLs pour d'Annam: {len(dannam_urls)}")
    
    if dannam_urls:
        print("\nPremières URLs d'Annam:")
        for url in dannam_urls[:5]:
            print(f"  - {url['perfume_url']}")
    
    # Vérifier les doublons
    print("\n🔍 Vérification des doublons...")
    all_urls = [
        doc['perfume_url'] 
        for doc in db.perfume_urls.find({}, {"perfume_url": 1, "_id": 0})
    ]
    unique_urls = set(all_urls)
    
    if len(all_urls) != len(unique_urls):
        print(f"\n⚠️  ATTENTION : {len(all_urls) - len(unique_urls)} URLs en double!")
        
        # Trouver les doublons
        from collections import Counter
        duplicates = [url for url, count in Counter(all_urls).items() if count > 1]
        print(f"\nExemples de doublons:")
        for url in duplicates[:5]:
            count = Counter(all_urls)[url]
            print(f"  - {url} (apparaît {count} fois)")
    else:
        print("\n✅ Aucun doublon détecté")
    
    # Statistiques par designer
    print("\n📊 Top 5 designers par nombre d'URLs:")
    pipeline = [
        {"$group": {"_id": "$designer", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    for i, doc in enumerate(db.perfume_urls.aggregate(pipeline), 1):
        print(f"  {i}. {doc['_id']}: {doc['count']:,} URLs")
    
    client.close()
    print("\n✅ Diagnostic terminé avec succès")

except Exception as e:
    print(f"❌ Erreur de connexion MongoDB: {e}")
    print("\n💡 Assurez-vous que MongoDB est démarré:")
    print("   docker-compose up -d mongodb")
    import traceback
    traceback.print_exc()