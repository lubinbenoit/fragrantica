#!/usr/bin/env python3
"""Script de diagnostic des URLs"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@localhost:27017/')
client = MongoClient(mongo_uri)
db = client['fragrantica']

print("=== Diagnostic MongoDB ===\n")

# Total URLs
total = db.perfume_urls.count_documents({})
print(f"Total URLs: {total:,}\n")

# URLs pour d'Annam
dannam_urls = list(db.perfume_urls.find({"designer": "d'Annam"}, {"perfume_url": 1, "_id": 0}))
print(f"URLs pour d'Annam: {len(dannam_urls)}")

if dannam_urls:
    print("\nPremières URLs d'Annam:")
    for url in dannam_urls[:5]:
        print(f"  - {url['perfume_url']}")

# Vérifier les doublons
all_urls = [doc['perfume_url'] for doc in db.perfume_urls.find({}, {"perfume_url": 1, "_id": 0})]
unique_urls = set(all_urls)

if len(all_urls) != len(unique_urls):
    print(f"\n⚠️  ATTENTION : {len(all_urls) - len(unique_urls)} URLs en double!")
    
    # Trouver les doublons
    from collections import Counter
    duplicates = [url for url, count in Counter(all_urls).items() if count > 1]
    print(f"\nExemples de doublons:")
    for url in duplicates[:5]:
        print(f"  - {url} (apparaît {Counter(all_urls)[url]} fois)")
else:
    print("\n✅ Aucun doublon détecté")

client.close()