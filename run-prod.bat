@echo off
chcp 65001 >nul
cls
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║         Jamali Parfum — MODE PRODUCTION              ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: ─── Vérif Docker ───────────────────────────────────────────
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker n'est pas installe ou Docker Desktop n'est pas ouvert.
    echo Ouvre Docker Desktop et relance ce script.
    pause & exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Compose plugin introuvable.
    pause & exit /b 1
)

:: ─── Vérif .env ─────────────────────────────────────────────
if not exist ".env" (
    echo [ERREUR] Fichier .env manquant !
    echo Cree un fichier .env avec MONGO_URI, GEMINI_API_KEY, etc.
    pause & exit /b 1
)

echo [OK] Docker OK.
echo [OK] .env OK.
echo.

:: ─── Choisir l'action ───────────────────────────────────────
echo Que veux-tu faire ?
echo   [1] Demarrer la prod (docker compose up)
echo   [2] Rebuild + Demarrer (--build)
echo   [3] Arreter tous les services
echo   [4] Voir les logs en live
echo   [5] Statut des conteneurs
echo.
set /p CHOIX="Ton choix [1-5] : "

if "%CHOIX%"=="1" goto START
if "%CHOIX%"=="2" goto REBUILD
if "%CHOIX%"=="3" goto STOP
if "%CHOIX%"=="4" goto LOGS
if "%CHOIX%"=="5" goto STATUS
echo [ERREUR] Choix invalide.
pause & exit /b 1

:START
echo.
echo [INFO] Demarrage des conteneurs (Flask + MongoDB + Nginx)...
docker compose up -d
goto CHECK

:REBUILD
echo.
echo [INFO] Rebuild de l'image Flask + demarrage...
docker compose build --no-cache jamali-flask
docker compose up -d
goto CHECK

:STOP
echo.
echo [INFO] Arret de tous les services Jamali...
docker compose down
echo [OK] Services arretes.
pause & exit /b 0

:LOGS
echo.
echo [INFO] Logs en live (Ctrl+C pour quitter)...
docker compose logs -f
pause & exit /b 0

:STATUS
echo.
docker compose ps
echo.
pause & exit /b 0

:CHECK
echo.
echo [INFO] Attente du demarrage (max 60s)...
set WAIT=0
:LOOP
timeout /t 3 >nul
set /a WAIT+=3
curl -sf http://localhost:8080/ >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [OK] Jamali Parfum est en ligne !
    echo.
    echo   Storefront : http://localhost:8080
    echo   Admin CMS  : http://localhost:8080/admin
    echo   API Status : http://localhost:8080/api/status
    echo.
    start http://localhost:8080
    pause & exit /b 0
)
if %WAIT% lss 60 (
    echo|set /p="."
    goto LOOP
)
echo.
echo [WARN] Timeout. Verifie les logs :
echo   docker compose logs jamali-flask
echo   docker compose logs jamali-mongo
docker compose ps
pause
