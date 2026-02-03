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
    echo.
    echo ATTENTION: Verifiez les parametres dans .env avant de continuer
    pause
)

REM Créer les dossiers de données
if not exist data mkdir data
if not exist crawls mkdir crawls
if not exist logs mkdir logs

REM Vérifier que Docker est actif
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Docker n'est pas demarre
    echo Lancez Docker Desktop et reessayez
    pause
    exit /b 1
)

REM Construire et démarrer tous les services
echo Construction des images Docker...
docker-compose build

echo.
echo Demarrage de MongoDB et Mongo Express...
docker-compose up -d mongodb mongo-express

echo.
echo Attente que MongoDB soit pret (15 secondes)...
timeout /t 15 /nobreak >nul

REM Vérifier que MongoDB est prêt
echo.
echo Verification de MongoDB...
docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] MongoDB est pret
) else (
    echo [AVERTISSEMENT] MongoDB pourrait ne pas etre completement pret
    echo Continuation quand meme...
)

echo.
echo Lancement du scraper...
docker-compose up scraper

echo.
echo ======================================
echo Scraping termine !
echo ======================================
echo.
echo Pour voir les stats:
echo    docker-compose exec scraper python run_scrapers.py --stats
echo.
echo Interface MongoDB:
echo    http://localhost:8081
echo    User: admin / Pass: pass
echo.
echo Pour arreter les services:
echo    docker-compose down
echo.
echo Pour nettoyer completement (supprime les donnees):
echo    docker-compose down -v
echo.
pause