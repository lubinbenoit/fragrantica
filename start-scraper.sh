#!/bin/bash
# ========================================
# Fragrantica Scraper - Docker Mode
# ========================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "======================================"
echo "Fragrantica Scraper - Docker Mode"
echo "======================================"
echo ""

# Vérifier que Docker Desktop est démarré
echo "Vérification de Docker Desktop..."
if ! docker info &> /dev/null; then
    echo "[ERREUR] Docker Desktop n'est pas démarré"
    echo ""
    echo "Action requise:"
    echo "  1. Lancez Docker Desktop"
    echo "  2. Attendez que Docker soit prêt"
    echo "  3. Relancez ce script"
    echo ""
    exit 1
fi
echo "OK - Docker Desktop est actif"
echo ""

# Créer .env si nécessaire
if [ ! -f .env ]; then
    echo "Création du fichier .env..."
    cp .env.example .env
    echo "[OK] Fichier .env créé"
    echo ""
    echo "ATTENTION: Vérifiez les paramètres dans .env avant de continuer"
    echo "Appuyez sur Entrée pour continuer..."
    read
fi

# Créer les dossiers de données
mkdir -p data crawls logs
echo "[OK] Dossiers de données créés"

# Construire et démarrer tous les services
echo ""
echo "Construction des images Docker..."
if ! docker compose build; then
    echo "[ERREUR] Échec de la construction"
    exit 1
fi

echo ""
echo "Démarrage de MongoDB et Mongo Express..."
if ! docker compose up -d mongodb mongo-express; then
    echo "[ERREUR] Échec du démarrage de MongoDB"
    exit 1
fi

echo ""
echo "Attente que MongoDB soit prêt (15 secondes)..."
sleep 15

# Vérifier que MongoDB est prêt
echo ""
echo "Vérification de MongoDB..."
if docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" &> /dev/null; then
    echo "[OK] MongoDB est prêt"
else
    echo "[AVERTISSEMENT] MongoDB pourrait ne pas être complètement prêt"
    echo "Continuation quand même..."
fi

echo ""
echo "Lancement du scraper..."
docker compose up scraper

echo ""
echo "======================================"
echo "Scraping terminé !"
echo "======================================"
echo ""
echo "Pour voir les stats:"
echo "   docker compose exec scraper python run_scrapers.py --stats"
echo ""
echo "Interface MongoDB:"
echo "   http://localhost:8081"
echo "   User: admin / Pass: pass"
echo ""
echo "Pour arrêter les services:"
echo "   docker compose down"
echo ""
echo "Pour nettoyer complètement (supprime les données):"
echo "   docker compose down -v"
echo ""
echo "Appuyez sur Entrée pour continuer..."
read