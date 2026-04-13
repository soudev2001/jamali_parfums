#!/bin/bash
# =============================================================
# deploy.sh — Déploiement Jamali Parfum sur Ubuntu
# Usage :
#   bash deploy.sh                  → Stack complète (port 8080)
#   bash deploy.sh --integrate-sarfx → Intègre sarfx-nginx existant
#   bash deploy.sh --no-cache       → Force rebuild complet
# =============================================================
set -euo pipefail

# ─── BuildKit : builds parallèles et couche de cache ──────────
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

NO_CACHE_FLAG=""
INTEGRATE_SARFX=false
for arg in "$@"; do
  [[ "$arg" == "--no-cache" ]]        && NO_CACHE_FLAG="--no-cache"
  [[ "$arg" == "--integrate-sarfx" ]] && INTEGRATE_SARFX=true
done

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${YELLOW}▶  $*${NC}"; }
success() { echo -e "${GREEN}✅  $*${NC}"; }
error()   { echo -e "${RED}❌  $*${NC}"; exit 1; }

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║     Jamali Parfum — Script de déploiement    ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Pré-requis ───────────────────────────────────────────────
command -v docker >/dev/null 2>&1 || error "Docker n'est pas installé."
docker compose version >/dev/null 2>&1 || error "Docker Compose (plugin) n'est pas installé."

# ─── Fichier .env ─────────────────────────────────────────────
if [ ! -f .env ]; then
  info "Aucun fichier .env trouvé. Copie depuis .env.example..."
  cp .env.example .env
  echo ""
  echo -e "${RED}⚠️  IMPORTANT : Éditez le fichier .env avec vos vraies clés API avant de continuer.${NC}"
  echo "   nano .env"
  echo ""
  read -r -p "Appuyez sur Entrée une fois le .env configuré..."
fi

# ─── Build & démarrage ────────────────────────────────────────
info "Récupération des images de base Docker..."
docker compose pull --ignore-pull-failures 2>/dev/null || true

info "Construction de l'image Flask (BuildKit activé)${NO_CACHE_FLAG:+ — sans cache}..."
# shellcheck disable=SC2086
docker compose build $NO_CACHE_FLAG jamali-flask

info "Démarrage des services Jamali (MongoDB, Flask, Nginx)..."
docker compose up -d

info "Attente de la disponibilité des services..."
MAX_WAIT=90
ELAPSED=0
until curl -sf http://localhost:8080/ > /dev/null 2>&1 || [ "$ELAPSED" -ge "$MAX_WAIT" ]; do
  sleep 3
  ELAPSED=$((ELAPSED + 3))
  echo -n "."
done
echo ""
if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
  info "Timeout — vérifiez les logs : docker compose logs jamali-flask"
else
  success "Services disponibles en ${ELAPSED}s."
fi

# ─── Santé des services ───────────────────────────────────────
echo ""
echo "═══ État des conteneurs Jamali ═══"
docker compose ps
echo ""

# Test Flask
if curl -sf http://localhost:8080/ > /dev/null 2>&1; then
  success "Jamali répond sur le port 8080."
else
  info "Flask démarre encore, vérifiez les logs : docker compose logs jamali-flask"
fi

# ─── Intégration sarfx-nginx (optionnel) ─────────────────────
if [[ "$INTEGRATE_SARFX" == true ]]; then
  echo ""
  info "Intégration avec sarfx-nginx..."

  if ! docker ps --format '{{.Names}}' | grep -q "^sarfx-nginx$"; then
    error "Le conteneur sarfx-nginx n'est pas en cours d'exécution."
  fi

  # Détection du réseau sarfx-nginx
  SARFX_NETWORK=$(docker inspect sarfx-nginx \
    --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
    | tr ' ' '\n' | grep -v '^$' | head -1)
  info "Réseau sarfx-nginx détecté : $SARFX_NETWORK"

  # Connecter jamali-flask au réseau sarfx
  docker network connect "$SARFX_NETWORK" jamali-flask 2>/dev/null \
    && info "jamali-flask connecté à $SARFX_NETWORK" \
    || info "jamali-flask déjà connecté."

  # Générer la config nginx pour sarfx
  cat > /tmp/jamali_vhost.conf << 'NGINXEOF'
# ─── Virtual host Jamali Parfum ──────────────
upstream jamali_backend {
    server jamali-flask:5000;
}

server {
    listen 80;
    server_name jamaliparfums.sarfx.io;

    server_tokens off;

    location / {
        # Frontend statique servi par jamali-nginx interne sur port 80
        proxy_pass         http://jamali-nginx:80;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

  # Copie dans sarfx-nginx
  docker cp /tmp/jamali_vhost.conf sarfx-nginx:/etc/nginx/conf.d/jamali.conf
  docker network connect "$SARFX_NETWORK" jamali-nginx 2>/dev/null || true

  # Test et rechargement
  docker exec sarfx-nginx nginx -t \
    && docker exec sarfx-nginx nginx -s reload \
    && success "sarfx-nginx rechargé avec la config Jamali." \
    || error "Erreur dans la config nginx. Vérifiez : docker exec sarfx-nginx nginx -t"
fi

# ─── Résumé ───────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Déploiement terminé !                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  📍 Boutique            : ${YELLOW}https://jamaliparfums.sarfx.io${NC}"
echo -e "  🔐 Admin CMS           : ${YELLOW}https://jamaliparfums.sarfx.io/admin${NC}"
echo ""
echo -e "  Commandes utiles :"
echo -e "    Logs Flask  : docker compose logs -f jamali-flask"
echo -e "    Logs Nginx  : docker compose logs -f jamali-nginx"
echo -e "    Logs MongoDB: docker compose logs -f jamali-mongo"
echo -e "    Arrêter     : docker compose down"
echo -e "    Redémarrer  : docker compose restart"
echo ""
if [[ "$INTEGRATE_SARFX" != true ]]; then
  echo -e "  ℹ️  Pour intégrer dans sarfx-nginx (port 80) :"
  echo -e "    ${YELLOW}bash deploy.sh --integrate-sarfx${NC}"
  echo -e "  ℹ️  Pour forcer rebuild complet :"
  echo -e "    ${YELLOW}bash deploy.sh --no-cache${NC}"
  echo ""
fi
