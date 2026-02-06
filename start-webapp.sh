#!/bin/bash
# ========================================
# Installation Fragrantica Webapp
# ========================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "============================================"
echo " Fragrantica Explorer - Installation"
echo "============================================"
echo ""

# Fonction pour vérifier une commande
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "ERREUR: $1 n'est pas installé"
        exit 1
    fi
}

# Vérifier que Docker Desktop est démarré
echo "[1/6] Vérification de Docker Desktop..."
if ! docker info &> /dev/null; then
    echo "ERREUR: Docker Desktop n'est pas démarré"
    echo ""
    echo "Action requise:"
    echo "  1. Lancez Docker Desktop"
    echo "  2. Attendez que Docker soit prêt"
    echo "  3. Relancez ce script"
    echo ""
    exit 1
fi
echo "OK - Docker Desktop est actif"

# Vérifier Docker
echo "[2/6] Vérification de Docker..."
check_command docker
echo "OK - Docker est installé"

# Vérifier Docker Compose
echo "[3/6] Vérification de Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo "ERREUR: Docker Compose n'est pas disponible"
    exit 1
fi
echo "OK - Docker Compose est installé"

# Copier .env si nécessaire
echo "[4/6] Configuration de l'environnement..."
if [ ! -f .env ]; then
    echo "Création du fichier .env..."
    cp .env.example .env
    echo "OK - Fichier .env créé"
    echo ""
    echo "ATTENTION: Vérifiez les paramètres dans .env si nécessaire"
    echo ""
else
    echo "OK - Fichier .env existe déjà"
fi

# Construire les images
echo "[5/6] Construction des images Docker..."
if ! docker compose build webapp; then
    echo "ERREUR: Échec de la construction"
    exit 1
fi
echo "OK - Images construites"

# Démarrer les services
echo "[6/6] Démarrage des services..."
if ! docker compose up -d; then
    echo "ERREUR: Échec du démarrage"
    exit 1
fi
echo "OK - Services démarrés"

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
echo "  - Voir les logs:     docker compose logs -f webapp"
echo "  - Arrêter:          docker compose down"
echo "  - Redémarrer:       docker compose restart webapp"
echo ""

# Ouvrir le navigateur (selon l'OS)
echo "Ouverture du navigateur dans 3 secondes..."
sleep 3

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:5000 2>/dev/null || true
fi

echo ""
echo "Appuyez sur Entrée pour continuer..."
read