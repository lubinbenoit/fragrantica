@echo off
REM ========================================
REM Fragrantica Scraper - Docker Mode
REM ========================================
echo.
echo ======================================
echo Fragrantica Scraper - Docker Mode
echo ======================================
echo.

REM Verifier que Docker Desktop est demarre
echo Verification de Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Desktop n'est pas demarre
    echo.
    echo Action requise:
    echo   1. Lancez Docker Desktop depuis le menu Windows
    echo   2. Attendez que l'icone affiche "Docker Desktop is running"
    echo   3. Relancez ce script
    echo.
    pause
    exit /b 1
)
echo OK - Docker Desktop est actif
echo.

REM Creer .env si necessaire
if not exist .env (
    echo Creation du fichier .env...
    copy .env.example .env
    echo [OK] Fichier .env cree
    echo.
    echo ATTENTION: Verifiez les parametres dans .env avant de continuer
    pause
)

REM Creer les dossiers de donnees
if not exist data mkdir data
if not exist crawls mkdir crawls
if not exist logs mkdir logs
echo [OK] Dossiers de donnees crees

REM Construire et demarrer tous les services
echo.
echo Construction des images Docker...
docker compose build
if errorlevel 1 (
    echo [ERREUR] Echec de la construction
    pause
    exit /b 1
)

echo.
echo Demarrage de MongoDB et Mongo Express...
docker compose up -d mongodb mongo-express
if errorlevel 1 (
    echo [ERREUR] Echec du demarrage de MongoDB
    pause
    exit /b 1
)

echo.
echo Attente que MongoDB soit pret (15 secondes)...
timeout /t 15 /nobreak >nul

REM Verifier que MongoDB est pret
echo.
echo Verification de MongoDB...
docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] MongoDB est pret
) else (
    echo [AVERTISSEMENT] MongoDB pourrait ne pas etre completement pret
    echo Continuation quand meme...
)

echo.
echo Lancement du scraper...
docker compose up scraper

echo.
echo ======================================
echo Scraping termine !
echo ======================================
echo.
echo Pour voir les stats:
echo    docker compose exec scraper python run_scrapers.py --stats
echo.
echo Interface MongoDB:
echo    http://localhost:8081
echo    User: admin / Pass: pass
echo.
echo Pour arreter les services:
echo    docker compose down
echo.
echo Pour nettoyer completement (supprime les donnees):
echo    docker compose down -v
echo.
pause