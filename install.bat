@echo off
REM ========================================
REM Installation Fragrantica Webapp
REM ========================================

echo.
echo ============================================
echo  Fragrantica Explorer - Installation
echo ============================================
echo.

REM Verifier Docker
echo [1/5] Verification de Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker n'est pas installe ou n'est pas dans le PATH
    echo Installez Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo OK - Docker est installe

REM Verifier Docker Compose
echo [2/5] Verification de Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker Compose n'est pas installe
    pause
    exit /b 1
)
echo OK - Docker Compose est installe

REM Copier .env si necessaire
echo [3/5] Configuration de l'environnement...
if not exist .env (
    echo Creation du fichier .env...
    copy .env.example .env
    echo OK - Fichier .env cree
) else (
    echo OK - Fichier .env existe deja
)

REM Construire les images
echo [4/5] Construction des images Docker...
docker-compose build webapp
if errorlevel 1 (
    echo ERREUR: Echec de la construction
    pause
    exit /b 1
)
echo OK - Images construites

REM Demarrer les services
echo [5/5] Demarrage des services...
docker-compose up -d
if errorlevel 1 (
    echo ERREUR: Echec du demarrage
    pause
    exit /b 1
)
echo OK - Services demarres

echo.
echo ============================================
echo  Installation terminee !
echo ============================================
echo.
echo Services disponibles:
echo   - Webapp:        http://localhost:5000
echo   - Mongo Express: http://localhost:8081 (admin/pass)
echo.
echo Commandes utiles:
echo   - Voir les logs:     docker-compose logs -f webapp
echo   - Arreter:          docker-compose down
echo   - Redemarrer:       docker-compose restart
echo.

REM Ouvrir le navigateur
echo Ouverture du navigateur...
timeout /t 3 >nul
start http://localhost:5000

echo.
pause