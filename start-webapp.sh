#!/bin/bash

# ========================================
# Installation Fragrantica Webapp
# ========================================

set -e

echo ""
echo "============================================"
echo " Fragrantica Explorer - Installation"
echo "============================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'erreur
error() {
    echo -e "${RED}ERREUR: $1${NC}"
    exit 1
}

# Fonction de succès
success() {
    echo -e "${GREEN}OK - $1${NC}"
}

# Fonction d'information
info() {
    echo -e "${YELLOW}$1${NC}"
}

# 1. Vérifier Docker
echo "[1/5] Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Installez-le: https://docs.docker.com/get-docker/"
fi
success "Docker est installé"

# 2. Vérifier Docker Compose
echo "[2/5] Vérification de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose n'est pas installé"
fi
success "Docker Compose est installé"

# 3. Créer .env si nécessaire
echo "[3/5] Configuration de l'environnement..."
if [ ! -f .env ]; then
    info "Création du fichier .env..."
    cp .env.example .env
    success "Fichier .env créé"
else
    success "Fichier .env existe déjà"
fi

# 4. Construire les images
echo "[4/5] Construction des images Docker..."
docker-compose build webapp || error "Échec de la construction"
success "Images construites"

# 5. Démarrer les services
echo "[5/5] Démarrage des services..."
docker-compose up -d || error "Échec du démarrage"
success "Services démarrés"

echo ""
echo "============================================"
echo " Installation terminée !"
echo "============================================"
echo ""
echo "Services disponibles:"
echo "  - Webapp:        http://localhost:5000"
echo "  - Mongo Express: http://localhost:8081 (admin/pass)"
echo ""
echo "Commandes utiles:"
echo "  - Voir les logs:     docker-compose logs -f webapp"
echo "  - Arrêter:          docker-compose down"
echo "  - Redémarrer:       docker-compose restart"
echo ""

# Attendre que les services soient prêts
info "Attente du démarrage des services..."
sleep 5

# Ouvrir le navigateur (selon l'OS)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000
elif command -v open &> /dev/null; then
    open http://localhost:5000
fi

echo ""
info "Appuyez sur Entrée pour continuer..."
read