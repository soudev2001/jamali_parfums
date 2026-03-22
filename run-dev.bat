@echo off
chcp 65001 >nul
cls
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║         Jamali Parfum — MODE DEVELOPPEMENT           ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: ─── Vérif Python ───────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    pause & exit /b 1
)

:: ─── Vérif .env ─────────────────────────────────────────────
if not exist ".env" (
    echo [WARN] Pas de fichier .env — creation depuis .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env cree. Edite-le avec tes vraies cles si besoin.
    ) else (
        echo [WARN] Ni .env ni .env.example trouves — demarrage sans config.
    )
)

:: ─── Installer les dependances ──────────────────────────────
echo [INFO] Verification des dependances pip...
pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause & exit /b 1
)
echo [OK] Dependances OK.
echo.

:: ─── Lancer Flask en mode DEBUG ─────────────────────────────
echo [INFO] Demarrage Flask (DEBUG mode) sur http://localhost:5001
echo [INFO] Ctrl+C pour arreter.
echo.
set FLASK_ENV=development
set FLASK_DEBUG=1
set PORT=5001

:: Tente d'ouvrir le navigateur après 2s
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:5001"

python app.py

echo.
echo [INFO] Serveur arrete.
pause
