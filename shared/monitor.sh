#!/bin/bash
# 24h site monitor — runs on Hengchuang server via cron
LOG=/var/log/site-monitor.log

SITES=(
  "www.jycsd.com"
  "healthy.jycsd.com"
  "pets.jycsd.com"
  "home.jycsd.com"
  "finance.jycsd.com"
  "tech.jycsd.com"
  "travel.jycsd.com"
)

check_site() {
  local url=$1
  local code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "https://$url" 2>/dev/null)
  if [ "$code" != "200" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $url returned $code" >> "$LOG"
  fi
}

for site in "${SITES[@]}"; do
  check_site "$site"
done
