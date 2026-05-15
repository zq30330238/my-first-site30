#!/bin/bash
# Weekly sync: git pull latest + deploy all sites to Cloudflare Pages
LOG=/var/log/site-monitor.log
REPO=/opt/jycsd-sites

[ -d "$REPO" ] || git clone https://github.com/zq30330238/my-first-site30.git "$REPO"

cd "$REPO"
git pull origin master 2>&1 | tail -3

[ -f /root/.cf-token ] && source /root/.cf-token

PROJECTS=(
  "main-site:main-site"
  "sub-healthy:healthy-jycsd"
  "sub-pets:pets-jycsd"
  "sub-home:home-jycsd"
  "sub-finance:finance-jycsd"
  "sub-tech:tech-jycsd"
  "sub-travel:travel-jycsd"
)

for pair in "${PROJECTS[@]}"; do
  dir="${pair%%:*}"
  proj="${pair##*:}"
  npx wrangler pages deploy "$dir" --project-name="$proj" --branch=master 2>&1 | grep -E "Success|Error" >> "$LOG"
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Weekly sync completed" >> "$LOG"
