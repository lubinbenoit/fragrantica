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
    echo ""
    echo "⚠️  ATTENTION: Vérifiez les paramètres dans .env avant de continuer"
    read -p "Appuyez sur Entrée pour continuer..."
fi

# Créer les dossiers de données
mkdir -p data crawls logs

# Vérifier que Docker est actif
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré"
    echo "   Lancez Docker et réessayez"
    exit 1
fi

# Construire et démarrer tous les services
echo "🏗️  Construction des images Docker..."
docker-compose build

echo ""
echo "🚀 Démarrage de MongoDB et Mongo Express..."
docker-compose up -d mongodb mongo-express

echo ""
echo "⏳ Attente que MongoDB soit prêt (15 secondes)..."
sleep 15

# Vérifier que MongoDB est prêt
echo ""
echo "🔍 Vérification de MongoDB..."
if docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB est prêt"
else
    echo "⚠️  MongoDB pourrait ne pas être complètement prêt"
    echo "   Continuation quand même..."
fi

echo ""
echo "🕷️  Lancement du scraper..."
docker-compose up scraper

echo ""
echo "======================================"
echo "✅ Scraping terminé !"
echo "======================================"
echo ""
echo "📊 Pour voir les stats:"
echo "   docker-compose exec scraper python run_scrapers.py --stats"
echo ""
echo "🌐 Interface MongoDB:"
echo "   http://localhost:8081"
echo "   User: admin / Pass: pass"
echo ""
echo "🛑 Pour arrêter les services:"
echo "   docker-compose down"
echo ""
echo "🧹 Pour nettoyer complètement (supprime les données):"
echo "   docker-compose down -v"
echo ""