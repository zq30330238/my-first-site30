#!/bin/bash
# Daily SEO audit
LOG=/var/log/site-monitor.log
REPO=/opt/jycsd-sites

cd "$REPO"
git pull origin master -q 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SEO audit:" >> "$LOG"
python3 shared/seo_audit.py 2>&1 | tail -20 >> "$LOG"
echo "---" >> "$LOG"
