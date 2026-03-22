#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Jamali Parfum — Lanceur DEV (Linux / macOS / WSL)
#  Usage : bash run-dev.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         Jamali Parfum — MODE DÉVELOPPEMENT           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ─── Python ──────────────────────────────────────────────────
# Git Bash sur Windows utilise souvent "python" (pas python3)
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[ERREUR] Python introuvable. Installe Python 3.10+ et relance."
    exit 1
fi
PYTHON_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python $PYTHON_VER ($PYTHON)"

# ─── Virtualenv (Windows Git Bash + Linux/macOS) ─────────────
if [ ! -d ".venv" ]; then
    echo "[INFO] Création du virtualenv .venv..."
    $PYTHON -m venv .venv
fi
# Windows (Git Bash / MINGW) : Scripts/activate  |  Linux/macOS : bin/activate
if [ -f ".venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
    PYTHON=".venv/Scripts/python"
elif [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    PYTHON=".venv/bin/python"
else
    echo "[WARN] Impossible d'activer le virtualenv, utilisation du Python système."
fi
echo "[OK] Virtualenv activé"

# ─── Dépendances ─────────────────────────────────────────────
echo "[INFO] Installation des dépendances..."
$PYTHON -m pip install -r requirements.txt -q
echo "[OK] Dépendances installées"

# ─── .env ────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[INFO] .env créé depuis .env.example (vérifie les valeurs !)"
    else
        echo "[WARN] Pas de .env. Les fonctions MongoDB/IA seront désactivées."
    fi
else
    echo "[OK] .env trouvé"
fi

# ─── Variables Flask ─────────────────────────────────────────
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONDONTWRITEBYTECODE=1
export PORT=5001

echo ""
echo "  Storefront : http://localhost:5001"
  echo "  Admin CMS  : http://localhost:5001/admin"
  echo "  API Status : http://localhost:5001/api/status"
echo ""
echo "  (hot-reload activé — sauvegarde un fichier pour recharger)"
echo "  (Ctrl+C pour arrêter)"
echo ""

# ─── Ouvrir le navigateur (si disponible) ────────────────────
{
    sleep 2
    if command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:5001 &>/dev/null &
    elif command -v open &>/dev/null; then
        open http://localhost:5001 &>/dev/null &
    fi
} &

# ─── Démarrage Flask ─────────────────────────────────────────
$PYTHON app.py
