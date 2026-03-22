#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Jamali Parfum — Lanceur PRODUCTION (Linux / Ubuntu VPS)
#  Usage : bash run-prod.sh [--rebuild] [--stop] [--logs]
#
#  Pour un déploiement complet depuis zéro, utilise deploy.sh.
#  Ce script gère les opérations courantes en prod.
# ─────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

REBUILD=false
STOP=false
LOGS=false

for arg in "$@"; do
    case $arg in
        --rebuild) REBUILD=true ;;
        --stop)    STOP=true ;;
        --logs)    LOGS=true ;;
    esac
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         Jamali Parfum — MODE PRODUCTION              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ─── Prérequis ───────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    echo "[ERREUR] Docker non installé. Lance deploy.sh pour l'installation complète."
    exit 1
fi

if ! docker compose version &>/dev/null; then
    echo "[ERREUR] Docker Compose plugin manquant."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "[ERREUR] Fichier .env manquant !"
    echo "Crée-le depuis .env.example : cp .env.example .env"
    exit 1
fi

echo "[OK] Docker OK"
echo "[OK] .env OK"
echo ""

# ─── Arrêt ───────────────────────────────────────────────────
if $STOP; then
    echo "[INFO] Arrêt de tous les services..."
    docker compose down
    echo "[OK] Services arrêtés."
    exit 0
fi

# ─── Logs ────────────────────────────────────────────────────
if $LOGS; then
    echo "[INFO] Logs en live (Ctrl+C pour quitter)..."
    docker compose logs -f
    exit 0
fi

# ─── Démarrage / Rebuild ─────────────────────────────────────
if $REBUILD; then
    echo "[INFO] Rebuild de l'image Flask..."
    docker compose build --no-cache jamali-flask
fi

echo "[INFO] Démarrage des services (Flask + MongoDB + Nginx)..."
docker compose up -d

# ─── Attente santé ───────────────────────────────────────────
echo -n "[INFO] Attente démarrage"
WAIT=0
HEALTHY=false
while [ $WAIT -lt 60 ]; do
    sleep 3
    WAIT=$((WAIT + 3))
    if curl -sf http://localhost:8080/ &>/dev/null; then
        HEALTHY=true
        break
    fi
    echo -n "."
done
echo ""

if $HEALTHY; then
    echo ""
    echo "[OK] Jamali Parfum est en ligne !"
    echo ""
    echo "  Storefront : http://localhost:8080"
    echo "  Admin CMS  : http://localhost:8080/admin"
    echo "  API Status : http://localhost:8080/api/status"
    echo ""
    echo "Commandes utiles :"
    echo "  bash run-prod.sh --logs      # voir les logs"
    echo "  bash run-prod.sh --stop      # arrêter les services"
    echo "  bash run-prod.sh --rebuild   # rebuild + redémarrer"
    echo ""
else
    echo "[WARN] Le service ne répond pas encore. Vérifie les logs :"
    echo ""
    docker compose ps
    echo ""
    echo "  docker compose logs jamali-flask"
    echo "  docker compose logs jamali-mongo"
    exit 1
fi
