#!/usr/bin/env python3
"""
Script de lancement des scrapers Fragrantica avec gestion avancée.
Usage: python run_scrapers.py [--urls-only|--data-only|--stats]
"""

import sys
import subprocess
import argparse
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime


def run_command(cmd, description):
    """Exécute une commande et gère les erreurs."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} - Completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} - Failed with error code {e.returncode}")
        return False


def get_mongo_stats():
    """Affiche les statistiques MongoDB."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['fragrantica']
        
        urls_count = db.perfume_urls.count_documents({})
        data_count = db.perfume_data.count_documents({})
        
        print(f"\n{'='*60}")
        print("📊 MongoDB Statistics")
        print(f"{'='*60}")
        print(f"URLs collected:      {urls_count:,}")
        print(f"Perfumes scraped:    {data_count:,}")
        print(f"Remaining to scrape: {urls_count - data_count:,}")
        print(f"Progress:            {(data_count/urls_count*100):.1f}%" if urls_count > 0 else "Progress: 0%")
        print(f"{'='*60}\n")
        
        client.close()
    except Exception as e:
        print(f"⚠️  Could not fetch MongoDB stats: {e}")


def main():
    parser = argparse.ArgumentParser(description='Run Fragrantica scrapers')
    parser.add_argument('--urls-only', action='store_true', 
                       help='Only collect perfume URLs')
    parser.add_argument('--data-only', action='store_true', 
                       help='Only scrape perfume data')
    parser.add_argument('--stats', action='store_true', 
                       help='Show MongoDB statistics only')
    parser.add_argument('--resume', action='store_true', 
                       help='Resume interrupted scraping')
    
    args = parser.parse_args()
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path('scrapy.cfg').exists():
        print("❌ Error: scrapy.cfg not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Statistiques uniquement
    if args.stats:
        get_mongo_stats()
        sys.exit(0)
    
    print(f"\n🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Collecter les URLs
    if not args.data_only:
        success = run_command(
            "scrapy crawl perfume_urls",
            "Collecting perfume URLs"
        )
        if not success and not args.resume:
            sys.exit(1)
    
    # Scraper les données
    if not args.urls_only:
        success = run_command(
            "scrapy crawl perfume_data",
            "Scraping perfume data"
        )
        if not success:
            sys.exit(1)
    
    # Afficher les stats finales
    get_mongo_stats()
    
    print(f"\n🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 All tasks completed!\n")


if __name__ == "__main__":
    main()