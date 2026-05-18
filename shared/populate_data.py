"""Populate game_site_data.json with character, guide, and topic data."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "shared", "game_site_data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ========== Valorant ==========
data["valorant"]["characters"] = [
    {"name": "Jett", "role": "Duelist", "desc": "South Korean wind assassin. Master Jett dash mechanics, Cloudburst lineups, and Blade Storm ace strategies.", "image": "jett.png", "link": "/guides/agents/", "color": "#7dd3fc"},
    {"name": "Phoenix", "role": "Duelist", "desc": "UK fire duelist with self-heal. Learn Hot Hands positioning, Curveball flashes, and Run It Back entry tactics.", "image": "phoenix.png", "link": "/guides/agents/", "color": "#fb923c"},
    {"name": "Reyna", "role": "Duelist", "desc": "Mexican soul-devouring duelist. How to chain Dismiss invulnerability, Leer placement, and Empress snowball rounds.", "image": "reyna.png", "link": "/guides/agents/", "color": "#c084fc"},
    {"name": "Sage", "role": "Sentinel", "desc": "Chinese healer and controller. Wall boost spots, Slow Orb lineups, and Resurrection timing for maximum round impact.", "image": "sage.png", "link": "/guides/agents/", "color": "#4ade80"}
]
data["valorant"]["hot_topics"] = [
    {"title": "Best Agent Comps for Every Map (Patch 10.04)", "desc": "Which agents dominate each map in the current meta — complete breakdown with win rate data.", "image": "jett.png", "link": "/guides/agents/"},
    {"title": "Ultimate Aim Training Routine: Bronze to Radiant", "desc": "30-minute daily aim routine that improved over 10,000 players' headshot percentage by 15%.", "image": "phoenix.png", "link": "/guides/ranked/"},
    {"title": "Every Map Callout You Need to Know", "desc": "Complete callout guides for all 10 maps — communicate like a pro with your team.", "image": "reyna.png", "link": "/guides/maps/"}
]
data["valorant"]["guide_cards"] = [
    {"title": "Jett Main Guide: Movement Tech & Knife Tricks", "category": "Agents", "cat_color": "#ef4444", "date": "May 17, 2026", "image": "jett.png", "image_bg": "from-sky-900 to-blue-950", "link": "/guides/agents/"},
    {"title": "Phoenix Flash Lineups on Every Map", "category": "Lineups", "cat_color": "#22d3ee", "date": "May 16, 2026", "image": "phoenix.png", "image_bg": "from-orange-900 to-red-950", "link": "/guides/lineups/"},
    {"title": "Sage Wall Boosts: 50+ Off-Angle Spots", "category": "Agents", "cat_color": "#ef4444", "date": "May 15, 2026", "image": "sage.png", "image_bg": "from-emerald-900 to-green-950", "link": "/guides/agents/"},
    {"title": "Ranked Climb Guide: Silver to Diamond in 30 Days", "category": "Ranked", "cat_color": "#fbbf24", "date": "May 14, 2026", "image": "reyna.png", "image_bg": "from-purple-900 to-fuchsia-950", "link": "/guides/ranked/"}
]
data["valorant"]["categories"] = [
    {"name": "Agents", "slug": "agents", "color": "#ef4444", "character_img": "jett.png", "count": "24"},
    {"name": "Maps", "slug": "maps", "color": "#3b82f6", "character_img": "sage.png", "count": "10+"},
    {"name": "Weapons", "slug": "weapons", "color": "#a855f7", "character_img": "reyna.png", "count": "18"},
    {"name": "Ranked", "slug": "ranked", "color": "#fbbf24", "character_img": "phoenix.png", "count": "15+"},
    {"name": "Lineups", "slug": "lineups", "color": "#22d3ee", "character_img": "jett.png", "count": "30+"}
]

# ========== LoL ==========
data["lol"] = {
    "site_name": "LoLGuide",
    "domain": "lol.jycsd.com",
    "accent": "#fbbf24",
    "accent_dark": "#d97706",
    "tagline": "Dominate the Rift",
    "hero_title": "Season 2026 Meta",
    "hero_subtitle": "Complete champion guides, item builds, jungle pathing, and laning strategies for every role. Updated for the latest patch.",
    "quick_facts": {
        "Developer": "Riot Games",
        "First Release": "2009",
        "Platforms": "PC",
        "Game Genre": "MOBA",
        "Total Champions": "170+"
    },
    "characters": [
        {"name": "Ahri", "role": "Mid Lane Mage", "desc": "The nine-tailed fox. Charm combo sequences, Orb of Deception waveclear, and Spirit Rush roaming tactics for mid lane dominance.", "image": "ahri.png", "link": "/guides/champions/", "color": "#c084fc"},
        {"name": "Yasuo", "role": "Mid/Top Fighter", "desc": "The Unforgiven samurai. Steel Tempest mechanics, Wind Wall timing, and Last Breath knockup combos for solo carry potential.", "image": "yasuo.png", "link": "/guides/champions/", "color": "#60a5fa"},
        {"name": "Lux", "role": "Mid/Support Mage", "desc": "The Lady of Luminosity. Light binding picks, Prismatic Barrier teamfight tech, and Final Spark laser snipes from fog of war.", "image": "lux.png", "link": "/guides/champions/", "color": "#fbbf24"},
        {"name": "Jinx", "role": "ADC Marksman", "desc": "The Loose Cannon. Fishbones rocket form kiting, Zap root prediction, and Super Mega Death Rocket cross-map snipes.", "image": "jinx.png", "link": "/guides/champions/", "color": "#f472b6"}
    ],
    "categories": [
        {"name": "Champions", "slug": "champions", "color": "#fbbf24", "character_img": "ahri.png", "count": "170+"},
        {"name": "Items", "slug": "items", "color": "#3b82f6", "character_img": "yasuo.png", "count": "200+"},
        {"name": "Jungle", "slug": "jungle", "color": "#4ade80", "character_img": "jinx.png", "count": "15+"},
        {"name": "Laning", "slug": "laning", "color": "#a855f7", "character_img": "lux.png", "count": "12+"},
        {"name": "Teamfights", "slug": "teamfights", "color": "#ef4444", "character_img": "yasuo.png", "count": "20+"}
    ],
    "hot_topics": [
        {"title": "Best Champions to Climb in Season 2026 (Patch 14.9)", "desc": "Win rate and pick rate analysis for every role — which champions give you the best LP gains right now.", "image": "ahri.png", "link": "/guides/champions/"},
        {"title": "Complete Jungle Pathing Guide: Every Camp Clear", "desc": "Fastest level 3 and full clear routes for every meta jungler with leash and leashless starts.", "image": "jinx.png", "link": "/guides/jungle/"},
        {"title": "When to Roam vs Stay in Lane: A Data-Driven Guide", "desc": "Learn the exact wave states and timers that justify roaming — stop guessing and start climbing.", "image": "yasuo.png", "link": "/guides/laning/"}
    ],
    "guide_cards": [
        {"title": "Ahri Mid Guide: Runes, Builds & Matchup Spreadsheet", "category": "Champions", "cat_color": "#fbbf24", "date": "May 17, 2026", "image": "ahri.png", "image_bg": "from-purple-900 to-pink-950", "link": "/guides/champions/"},
        {"title": "Yasuo Mechanics: Airblade, Keyblade & Wall Dash", "category": "Champions", "cat_color": "#fbbf24", "date": "May 16, 2026", "image": "yasuo.png", "image_bg": "from-blue-900 to-cyan-950", "link": "/guides/champions/"},
        {"title": "ADC Positioning: Teamfight Survival Guide", "category": "Teamfights", "cat_color": "#ef4444", "date": "May 15, 2026", "image": "jinx.png", "image_bg": "from-pink-900 to-rose-950", "link": "/guides/teamfights/"},
        {"title": "Support Vision Control: Ward Score 100+ Every Game", "category": "Laning", "cat_color": "#a855f7", "date": "May 14, 2026", "image": "lux.png", "image_bg": "from-amber-900 to-yellow-950", "link": "/guides/laning/"}
    ],
    "footer_links": [
        {"text": "Valorant", "url": "https://valorant.jycsd.com"},
        {"text": "Fortnite", "url": "https://fortnite.jycsd.com"},
        {"text": "Minecraft", "url": "https://minecraft.jycsd.com"},
        {"text": "All Games", "url": "https://games.jycsd.com"}
    ]
}

# ========== Fortnite ==========
data["fortnite"]["hot_topics"] = [
    {"title": "Chapter 6 Season 3: Every New Weapon & POI", "desc": "Full breakdown of the new season — weapons, map changes, battle pass skins, and gameplay mechanics.", "link": "/guides/seasons/"},
    {"title": "Best Landing Spots for High Kills (Chapter 6 Map)", "desc": "Where to land for the best loot, most eliminations, and highest survival rate in Chapter 6.", "link": "/guides/map/"},
    {"title": "Zero Build Mode: Complete Strategy Guide", "desc": "How to win without building — positioning, rotation paths, and loadout priorities for Zero Build mode.", "link": "/guides/weapons/"}
]
data["fortnite"]["guide_cards"] = [
    {"title": "All Weapons Ranked: DPS Tier List Chapter 6 S3", "category": "Weapons", "cat_color": "#a78bfa", "date": "May 17, 2026", "image": "", "image_bg": "from-purple-900 to-indigo-950", "link": "/guides/weapons/"},
    {"title": "How to Get the Mythic Loot Pool: Full Quest Guide", "category": "Seasons", "cat_color": "#4ade80", "date": "May 16, 2026", "image": "", "image_bg": "from-emerald-900 to-green-950", "link": "/guides/seasons/"},
    {"title": "Pro Builder Edit Course: Master Piece Control", "category": "Building", "cat_color": "#fbbf24", "date": "May 15, 2026", "image": "", "image_bg": "from-amber-900 to-yellow-950", "link": "/guides/building/"},
    {"title": "Every Vault Location & How to Open Them", "category": "Map", "cat_color": "#22d3ee", "date": "May 14, 2026", "image": "", "image_bg": "from-cyan-900 to-sky-950", "link": "/guides/map/"}
]
data["fortnite"]["categories"] = [
    {"name": "Weapons", "slug": "weapons", "color": "#a78bfa", "count": "20+"},
    {"name": "Map", "slug": "map", "color": "#22d3ee", "count": "15+"},
    {"name": "Building", "slug": "building", "color": "#fbbf24", "count": "12+"},
    {"name": "Seasons", "slug": "seasons", "color": "#4ade80", "count": "30+"}
]

# ========== Elden Ring ==========
data["eldenring"]["hot_topics"] = [
    {"title": "Shadow of the Erdtree: Complete DLC Boss Guide", "desc": "Every remembrance boss in the Land of Shadow — movesets, weaknesses, summon strategies, and reward breakdown.", "link": "/guides/bosses/"},
    {"title": "Best Builds for NG+7: One-Shot Boss Killers", "desc": "The most broken PvE builds that still work at max scaling — bleed, magic, and faith builds ranked.", "link": "/guides/builds/"},
    {"title": "All Legendary Armaments & Where to Find Them", "desc": "Complete locations for every legendary weapon including the Dark Moon Greatsword and Ruins Greatsword.", "link": "/guides/weapons/"}
]
data["eldenring"]["guide_cards"] = [
    {"title": "Malenia Boss Guide: How to Dodge Waterfowl Dance", "category": "Bosses", "cat_color": "#ef4444", "date": "May 17, 2026", "image": "", "image_bg": "from-red-950 to-rose-950", "link": "/guides/bosses/"},
    {"title": "Ranni Questline: Age of Stars Ending Walkthrough", "category": "Quests", "cat_color": "#a78bfa", "date": "May 16, 2026", "image": "", "image_bg": "from-purple-900 to-indigo-950", "link": "/guides/quests/"},
    {"title": "Top 10 Bleed Builds That Melt Bosses in Seconds", "category": "Builds", "cat_color": "#fbbf24", "date": "May 15, 2026", "image": "", "image_bg": "from-amber-900 to-yellow-950", "link": "/guides/builds/"},
    {"title": "Every Somber Ancient Dragon Smithing Stone Location", "category": "Weapons", "cat_color": "#3b82f6", "date": "May 14, 2026", "image": "", "image_bg": "from-blue-900 to-sky-950", "link": "/guides/weapons/"}
]
data["eldenring"]["categories"] = [
    {"name": "Bosses", "slug": "bosses", "color": "#ef4444", "count": "165+"},
    {"name": "Builds", "slug": "builds", "color": "#fbbf24", "count": "40+"},
    {"name": "Weapons", "slug": "weapons", "color": "#3b82f6", "count": "300+"},
    {"name": "Quests", "slug": "quests", "color": "#a78bfa", "count": "30+"},
    {"name": "Map", "slug": "map", "color": "#4ade80", "count": "15"}
]

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK: game_site_data.json populated")
for k in ["minecraft", "valorant", "lol", "fortnite", "eldenring"]:
    d = data[k]
    print(f"  {k}: {len(d.get('characters',[]))} chars, {len(d.get('guide_cards',[]))} guides, {len(d.get('hot_topics',[]))} topics")
