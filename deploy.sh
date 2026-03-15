#!/bin/bash
# =============================================================
# deploy.sh — Déploiement Jamali Parfum sur Ubuntu
# Usage :
#   bash deploy.sh                  → Stack complète (port 8080)
#   bash deploy.sh --integrate-sarfx → Intègre sarfx-nginx existant
# =============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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
info "Construction de l'image Flask..."
docker compose build --no-cache jamali-flask

info "Démarrage des services Jamali (MongoDB, Flask, Nginx)..."
docker compose up -d

info "Attente de la disponibilité des services (30s)..."
sleep 30

# ─── Santé des services ───────────────────────────────────────
echo ""
echo "═══ État des conteneurs Jamali ═══"
docker compose ps
echo ""

# Test Flask
if curl -sf http://localhost:8080/api/ > /dev/null 2>&1 || curl -sf http://localhost:5000/ > /dev/null 2>&1; then
  success "Flask répond correctement."
else
  info "Flask démarre encore, vérifiez les logs : docker compose logs jamali-flask"
fi

# ─── Intégration sarfx-nginx (optionnel) ─────────────────────
if [[ "$1" == "--integrate-sarfx" ]]; then
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
# Remplacez "jamali.votredomaine.com" par votre vrai domaine
# ou commentez la ligne server_name pour utiliser l'IP seule.
upstream jamali_backend {
    server jamali-flask:5000;
}

server {
    listen 80;
    server_name jamali.votredomaine.com;

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
echo -e "  📍 Jamali Parfum (port dédié) : ${YELLOW}http://195.35.28.227:8080${NC}"
echo ""
echo -e "  Commandes utiles :"
echo -e "    Logs Flask  : docker compose logs -f jamali-flask"
echo -e "    Logs Nginx  : docker compose logs -f jamali-nginx"
echo -e "    Logs MongoDB: docker compose logs -f jamali-mongo"
echo -e "    Arrêter     : docker compose down"
echo -e "    Redémarrer  : docker compose restart"
echo ""
if [[ "$1" != "--integrate-sarfx" ]]; then
  echo -e "  ℹ️  Pour intégrer dans sarfx-nginx (port 80) :"
  echo -e "    ${YELLOW}bash deploy.sh --integrate-sarfx${NC}"
  echo ""
fi
