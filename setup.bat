@echo off
REM setup.bat - Script d'installation pour Windows

echo =============================
echo Fragrantica Scraper Setup
echo =============================
echo.

REM Vérifier Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [X] Docker n'est pas installe.
    echo    Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker detecte

REM Créer .env si n'existe pas
if not exist .env (
    echo Creation du fichier .env...
    copy .env.example .env
    echo [OK] Fichier .env cree
)

REM Créer le virtual environment Python
if not exist venv (
    echo Creation de l'environnement virtuel Python...
    python -m venv venv
)

REM Activer venv et installer les dépendances
echo Installation des dependances Python...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Créer les dossiers nécessaires
if not exist data mkdir data
if not exist crawls mkdir crawls

REM Démarrer MongoDB avec Docker
echo.
echo Demarrage de MongoDB...
docker-compose up -d

REM Attendre que MongoDB soit prêt
echo Attente du demarrage de MongoDB...
timeout /t 5 /nobreak >nul

echo.
echo =============================
echo Installation terminee !
echo =============================
echo.
echo Commandes utiles:
echo   - Lancer les scrapers:    .\run.bat
echo   - Voir les stats:         python scripts\mongo_utils.py stats
echo   - Interface web MongoDB:  http://localhost:8081
echo   - Arreter MongoDB:        docker-compose down
echo.
pause