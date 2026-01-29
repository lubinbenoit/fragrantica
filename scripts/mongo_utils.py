#!/usr/bin/env python3
"""
Utilitaires MongoDB pour le projet Fragrantica.
Usage: python scripts/mongo_utils.py [command]
"""

import json
import sys
import os
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# ✅ Charger les variables d'environnement
load_dotenv()


class MongoUtils:
    def __init__(self, uri=None, db_name=None):
        """
        Initialise la connexion MongoDB.
        Utilise les variables d'environnement si non spécifié.
        """
        # ✅ Priorité : paramètre > .env > défaut Docker
        self.uri = uri or os.getenv(
            'MONGO_URI', 
            'mongodb://admin:password123@localhost:27017/'
        )
        self.db_name = db_name or os.getenv('MONGO_DATABASE', 'fragrantica')
        
        print(f"🔗 Connecting to: {self.uri}")
        print(f"📂 Database: {self.db_name}\n")
        
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000
            )
            # Test de connexion
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\n💡 Make sure MongoDB is running:")
            print("   docker-compose up -d mongodb")
            sys.exit(1)
    
    def export_to_json(self, collection_name, output_file):
        """Exporte une collection MongoDB vers JSON."""
        print(f"📤 Exporting {collection_name} to {output_file}...")
        
        data = list(self.db[collection_name].find({}, {'_id': 0}))
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Exported {len(data):,} documents to {output_file}")
    
    def stats(self):
        """Affiche les statistiques détaillées."""
        print(f"\n{'='*70}")
        print("📊 Fragrantica MongoDB Statistics")
        print(f"{'='*70}\n")
        
        # URLs
        urls_count = self.db.perfume_urls.count_documents({})
        print(f"Perfume URLs collected:    {urls_count:,}")
        
        if urls_count > 0:
            brands = self.db.perfume_urls.distinct('designer')
            print(f"Unique brands:             {len(brands):,}")
        
        # Data
        data_count = self.db.perfume_data.count_documents({})
        print(f"\nPerfumes scraped:          {data_count:,}")
        
        if data_count > 0:
            # Marques les plus représentées
            pipeline = [
                {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            top_brands = list(self.db.perfume_data.aggregate(pipeline))
            
            print("\nTop 5 brands:")
            for i, brand in enumerate(top_brands, 1):
                print(f"  {i}. {brand['_id']}: {brand['count']:,} perfumes")
        
        # Progress
        if urls_count > 0:
            remaining = urls_count - data_count
            progress = (data_count / urls_count * 100) if urls_count > 0 else 0
            print(f"\n{'─'*70}")
            print(f"Remaining to scrape:       {remaining:,}")
            print(f"Progress:                  {progress:.1f}%")
            print(f"{'='*70}\n")
    
    def reset_collection(self, collection_name):
        """Vide une collection (avec confirmation)."""
        count = self.db[collection_name].count_documents({})
        
        if count == 0:
            print(f"Collection '{collection_name}' is already empty.")
            return
        
        confirm = input(
            f"⚠️  Are you sure you want to delete {count:,} documents "
            f"from '{collection_name}'? (yes/no): "
        )
        
        if confirm.lower() == 'yes':
            self.db[collection_name].delete_many({})
            print(f"✓ Collection '{collection_name}' cleared.")
        else:
            print("❌ Operation cancelled.")
    
    def close(self):
        """Ferme la connexion MongoDB."""
        self.client.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/mongo_utils.py [command]")
        print("\nCommands:")
        print("  stats              - Show database statistics")
        print("  export-urls        - Export URLs to JSON")
        print("  export-data        - Export perfume data to JSON")
        print("  export-all         - Export both collections")
        print("  reset-urls         - Clear URLs collection")
        print("  reset-data         - Clear data collection")
        sys.exit(1)
    
    command = sys.argv[1]
    utils = MongoUtils()  # ✅ Utilise automatiquement .env
    
    try:
        if command == 'stats':
            utils.stats()
        
        elif command == 'export-urls':
            utils.export_to_json('perfume_urls', 'data/perfume_urls.json')
        
        elif command == 'export-data':
            utils.export_to_json('perfume_data', 'data/perfume_data.json')
        
        elif command == 'export-all':
            utils.export_to_json('perfume_urls', 'data/perfume_urls.json')
            utils.export_to_json('perfume_data', 'data/perfume_data.json')
        
        elif command == 'reset-urls':
            utils.reset_collection('perfume_urls')
        
        elif command == 'reset-data':
            utils.reset_collection('perfume_data')
        
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    
    finally:
        utils.close()


if __name__ == "__main__":
    main()