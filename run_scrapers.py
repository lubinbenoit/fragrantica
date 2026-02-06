#!/usr/bin/env python3
"""
Script principal pour lancer les scrapers Fragrantica.
Usage: python run_scrapers.py [--urls-only|--data-only|--stats|--resume]
"""

import sys
import subprocess
import argparse
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()


def run_command(cmd, description):
    """Exécute une commande Scrapy et gère les erreurs."""
    print(f"\n{'='*70}")
    print(f"🚀 {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,  # Ne pas lever d'exception sur les codes d'erreur
            text=True
        )
        
        # Codes de sortie acceptables
        # 0 = succès complet
        # 1 = arrêt précoce mais gracieux (429, interruption, etc.)
        if result.returncode in (0, 1):
            if result.returncode == 0:
                print(f"\n✅ {description} - Terminé avec succès")
            else:
                print(f"\n⚠️  {description} - Arrêté prématurément (code {result.returncode})")
                print("    Les données collectées jusqu'ici ont été sauvegardées.")
            return True
        else:
            print(f"\n❌ {description} - Échec avec le code d'erreur {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        print("    Les données collectées jusqu'ici ont été sauvegardées.")
        return True  # Considérer comme succès partiel
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False


def get_mongo_stats():
    """Affiche les statistiques MongoDB."""
    try:
        # Valeur par défaut Docker-friendly
        mongo_uri = os.getenv(
            'MONGO_URI', 
            'mongodb://admin:password123@mongodb:27017/'
        )
        mongo_db = os.getenv('MONGO_DATABASE', 'fragrantica')
        
        print(f"🔗 Connecting to: {mongo_uri}")
        
        client = MongoClient(
            mongo_uri, 
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test de connexion
        client.admin.command('ping')
        db = client[mongo_db]
        
        urls_count = db.perfume_urls.count_documents({})
        data_count = db.perfume_data.count_documents({})
        
        print(f"\n{'='*70}")
        print("📊 Statistiques MongoDB")
        print(f"{'='*70}")
        print(f"URLs collectées:           {urls_count:,}")
        print(f"Parfums scrapés:           {data_count:,}")
        
        if urls_count > 0:
            remaining = urls_count - data_count
            progress = (data_count / urls_count * 100) if urls_count > 0 else 0
            print(f"Restant à scraper:         {remaining:,}")
            print(f"Progression:               {progress:.1f}%")
            
            # Designers les plus représentés
            pipeline = [
                {"$group": {"_id": "$designer", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            top_designers = list(db.perfume_urls.aggregate(pipeline))
            
            if top_designers:
                print(f"\nTop 5 designers (URLs):")
                for i, designer in enumerate(top_designers, 1):
                    print(f"  {i}. {designer['_id']}: {designer['count']:,} parfums")
        
        print(f"{'='*70}\n")
        
        client.close()
    except Exception as e:
        print(f"⚠️  Impossible de récupérer les stats MongoDB: {e}")
        import traceback
        traceback.print_exc()


def check_mongodb():
    """Vérifie que MongoDB est accessible."""
    try:
        # Valeur par défaut Docker-friendly
        mongo_uri = os.getenv(
            'MONGO_URI', 
            'mongodb://admin:password123@mongodb:27017/'
        )
        
        print(f"🔍 Checking MongoDB connection: {mongo_uri}")
        
        client = MongoClient(
            mongo_uri, 
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000
        )
        client.admin.command('ping')
        client.close()
        
        print("✅ MongoDB connection successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Erreur: MongoDB n'est pas accessible")
        print(f"   URI tentée: {os.getenv('MONGO_URI', 'non définie')}")
        print(f"   Détails: {e}")
        print(f"\n💡 Solution:")
        print(f"   - Si vous utilisez Docker: docker-compose up -d mongodb")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Lance les scrapers Fragrantica',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run_scrapers.py              # Exécute tout
  python run_scrapers.py --urls-only  # Collecte uniquement les URLs
  python run_scrapers.py --data-only  # Scrappe uniquement les données
  python run_scrapers.py --stats      # Affiche les statistiques
  python run_scrapers.py --resume     # Reprend après interruption
        """
    )
    
    parser.add_argument('--urls-only', action='store_true',
                       help='Collecte uniquement les URLs de parfums')
    parser.add_argument('--data-only', action='store_true',
                       help='Scrappe uniquement les données de parfums')
    parser.add_argument('--stats', action='store_true',
                       help='Affiche uniquement les statistiques MongoDB')
    parser.add_argument('--resume', action='store_true',
                       help='Reprend le scraping après interruption')
    
    args = parser.parse_args()
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path('scrapy.cfg').exists():
        print("❌ Erreur: scrapy.cfg introuvable.")
        print("   Exécutez ce script depuis la racine du projet.")
        sys.exit(1)
    
    # Vérifier MongoDB
    if not check_mongodb():
        sys.exit(1)
    
    # Statistiques uniquement
    if args.stats:
        get_mongo_stats()
        sys.exit(0)
    
    print(f"\n{'='*70}")
    print("🌸 Fragrantica Scraper")
    print(f"{'='*70}")
    print(f"🕐 Démarré à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # Statistiques avant
    get_mongo_stats()
    
    # Étape 1: Collecter les URLs
    if not args.data_only:
        success = run_command(
            "scrapy crawl perfume_urls",
            "Étape 1/2: Collection des URLs de parfums"
        )
        
        # Ne pas arrêter même en cas d'arrêt prématuré (429)
        # On continue avec les URLs qu'on a
        if not success:
            print("\n⚠️  La collection d'URLs a rencontré un problème")
            print("   Mais nous allons continuer avec les URLs déjà collectées...")
    
    # Étape 2: Scraper les données
    if not args.urls_only:
        success = run_command(
            "scrapy crawl perfume_data",
            "Étape 2/2: Scraping des données de parfums"
        )
        
        if not success:
            print("\n⚠️  Le scraping des données s'est arrêté")
            print("   Vous pouvez reprendre avec: python run_scrapers.py --data-only")
    
    # Statistiques finales
    print(f"\n{'='*70}")
    print("📊 Statistiques finales")
    print(f"{'='*70}")
    get_mongo_stats()
    
    print(f"🕐 Terminé à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        print("💡 Pour reprendre, lancez: python run_scrapers.py --resume\n")
        sys.exit(0)