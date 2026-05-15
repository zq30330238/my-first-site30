# PROJECT MAP (~200 tokens)

## Sites (7 total, each = independent Cloudflare Pages project)
```
main-site/       → jycsd.com            # brand nav
sub-healthy/     → healthy.jycsd.com    # nutrition, green theme
sub-pets/        → pets.jycsd.com       # pet care, orange theme
sub-home/        → home.jycsd.com       # home & garden
sub-finance/     → finance.jycsd.com    # personal finance
sub-tech/        → tech.jycsd.com       # tech & gadgets
sub-travel/      → travel.jycsd.com     # travel tips
```

## Per-site skeleton
```
sub-{name}/
├── index.html          # homepage, article cards
├── article-{n}.html    # 6+ articles per site
├── privacy-policy.html # legal (shared template)
├── terms-of-service.html
├── cookie-policy.html
├── robots.txt          # crawl rules
├── sitemap.xml         # XML sitemap
└── ads.txt             # AdSense verification
```

## Shared
```
shared/               # templates & checklists
.claude/skills/       # voice-chat, deploy, OCR, douyin parser
CLAUDE.md             # project rules (loaded every session)
```

## Stack
- Static HTML + Tailwind CDN + zero JS
- Deploy: `git push origin master` → Cloudflare Pages auto-deploy
- Monetization: Google AdSense (pending approval)

## Key constraints
- No frameworks, no build tools, no npm
- Each sub-site independent — changes don't cascade
- English content, 1000-1500 words/article, "core → detail → scenario" structure
