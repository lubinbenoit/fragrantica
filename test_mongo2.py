#!/usr/bin/env python3
"""Script de test de la présence d'URL dans MongoDB"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

client = MongoClient('mongodb://admin:password123@localhost:27017/')
db = client['fragrantica']

# Compter les URLs de d'Annam
count = db.perfume_urls.count_documents({"designer": "d'Annam"})
print(f"URLs de d'Annam en base: {count}")

# Afficher quelques URLs
urls = list(db.perfume_urls.find({"designer": "d'Annam"}, {"perfume_url": 1, "_id": 0}).limit(5))
print("Exemples d'URLs:")
for url in urls:
    print(f"  - {url['perfume_url']}")

client.close()