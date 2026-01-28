#!/bin/bash
# docker-run.sh - Lance le projet avec Docker

set -e

echo "======================================"
echo "🐳 Fragrantica Scraper - Docker Mode"
echo "======================================"
echo ""

# Créer .env si nécessaire
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✓ Fichier .env créé"
fi

# Créer les dossiers de données
mkdir -p data crawls logs

# Construire et démarrer tous les services
echo "🏗️  Construction des images Docker..."
docker-compose build

echo ""
echo "🚀 Démarrage des services..."
docker-compose up -d mongodb mongo-express

echo ""
echo "⏳ Attente que MongoDB soit prêt..."
sleep 10

echo ""
echo "🕷️  Lancement du scraper..."
docker-compose up scraper

echo ""
echo "======================================"
echo "✅ Scraping terminé !"
echo "======================================"
echo ""
echo "📊 Pour voir les stats:"
echo "   docker-compose run --rm scraper run_scrapers.py --stats"
echo ""
echo "🌐 Interface MongoDB:"
echo "   http://localhost:8081"
echo ""
echo "🛑 Pour arrêter les services:"
echo "   docker-compose down"
echo ""