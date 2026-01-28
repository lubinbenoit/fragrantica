@echo off
REM docker-run.bat - Lance le projet avec Docker

echo ======================================
echo Fragrantica Scraper - Docker Mode
echo ======================================
echo.

REM Créer .env si nécessaire
if not exist .env (
    echo Creation du fichier .env...
    copy .env.example .env
    echo [OK] Fichier .env cree
)

REM Créer les dossiers de données
if not exist data mkdir data
if not exist crawls mkdir crawls
if not exist logs mkdir logs

REM Construire et démarrer tous les services
echo Construction des images Docker...
docker-compose build

echo.
echo Demarrage des services...
docker-compose up -d mongodb mongo-express

echo.
echo Attente que MongoDB soit pret...
timeout /t 10 /nobreak >nul

echo.
echo Lancement du scraper...
docker-compose up scraper

echo.
echo ======================================
echo Scraping termine !
echo ======================================
echo.
echo Pour voir les stats:
echo    docker-compose run --rm scraper run_scrapers.py --stats
echo.
echo Interface MongoDB:
echo    http://localhost:8081
echo.
echo Pour arreter les services:
echo    docker-compose down
echo.
pause