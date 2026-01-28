#!/bin/bash
# setup.sh - Script d'installation pour le projet

set -e

echo "🚀 Fragrantica Scraper Setup"
echo "=============================="
echo ""

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé."
    echo "   Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

echo "✓ Docker détecté"

# Créer .env si n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✓ Fichier .env créé (vous pouvez le modifier si besoin)"
fi

# Créer le virtual environment Python
if [ ! -d "venv" ]; then
    echo "🐍 Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

# Activer venv et installer les dépendances
echo "📦 Installation des dépendances Python..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Créer les dossiers nécessaires
mkdir -p data
mkdir -p crawls

# Démarrer MongoDB avec Docker
echo ""
echo "🐳 Démarrage de MongoDB..."
docker-compose up -d

# Attendre que MongoDB soit prêt
echo "⏳ Attente du démarrage de MongoDB..."
sleep 5

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📚 Commandes utiles:"
echo "   - Lancer les scrapers:    ./run.sh"
echo "   - Voir les stats:         python scripts/mongo_utils.py stats"
echo "   - Interface web MongoDB:  http://localhost:8081"
echo "   - Arrêter MongoDB:        docker-compose down"
echo ""