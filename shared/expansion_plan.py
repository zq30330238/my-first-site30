"""
扩展计划 — 游戏矩阵 + 动漫矩阵
三个矩阵并列：生活(6站) + 游戏(N站) + 动漫(N站)
"""

GAME_MATRIX = {
    "portal": {
        "name": "GameGuide Hub",
        "domain": "games.jycsd.com",
        "brand": "GameGuide",
        "slogan": "Master Every Game",
        "desc": "Expert guides, character builds, and walkthroughs for the world's most popular games.",
    },
    "categories": {
        "sandbox-survival": {
            "label": "沙盒/生存",
            "color": "green",
            "games": {
                "minecraft": {
                    "priority": 1,
                    "domain": "minecraft.jycsd.com",
                    "brand": "MineGuide",
                    "sections": {
                        "crafting": "合成配方大全 — 工作台/熔炉/酿造台所有配方",
                        "mobs": "生物图鉴 — 所有生物属性/掉落/生成条件",
                        "building": "建筑攻略 — 房屋/农场/红石机械/装饰",
                        "redstone": "红石教程 — 基础电路到高级自动化",
                        "enchanting": "附魔指南 — 最优附魔组合/经验获取",
                        "biomes": "生物群系 — 每个群系的资源/结构/生存技巧",
                    },
                    "article_count": 120,
                },
                "terraria": {
                    "priority": 8,
                    "domain": "terraria.jycsd.com",
                    "brand": "TerrariaGuide",
                    "article_count": 80,
                },
                "palworld": {
                    "priority": 9,
                    "domain": "palworld.jycsd.com",
                    "brand": "PalGuide",
                    "article_count": 60,
                },
                "valheim": {
                    "priority": 12,
                    "domain": "valheim.jycsd.com",
                    "brand": "ValheimGuide",
                    "article_count": 50,
                },
            },
        },
        "open-world-rpg": {
            "label": "开放世界/RPG",
            "color": "amber",
            "games": {
                "elden-ring": {
                    "priority": 2,
                    "domain": "eldenring.jycsd.com",
                    "brand": "TarnishedGuide",
                    "sections": {
                        "bosses": "BOSS攻略 — 全BOSS打法/弱点/掉落",
                        "builds": "流派Build — 力敏智信各流派配装",
                        "weapons": "武器图鉴 — 全武器获取/战技/升级",
                        "quests": "支线攻略 — NPC任务链全流程",
                        "map": "地图指南 — 全区域收集/隐藏路线",
                    },
                    "article_count": 100,
                },
                "gta-6": {
                    "priority": 3,
                    "domain": "gta6.jycsd.com",
                    "brand": "GTA6Guide",
                    "article_count": 80,
                },
                "hogwarts-legacy": {
                    "priority": 7,
                    "domain": "hogwartslegacy.jycsd.com",
                    "brand": "HogwartsGuide",
                    "article_count": 70,
                },
                "baldurs-gate-3": {
                    "priority": 10,
                    "domain": "bg3.jycsd.com",
                    "brand": "BG3Guide",
                    "article_count": 90,
                },
                "cyberpunk-2077": {
                    "priority": 11,
                    "domain": "cyberpunk2077.jycsd.com",
                    "brand": "NightCityGuide",
                    "article_count": 70,
                },
            },
        },
        "competitive": {
            "label": "联机/电竞",
            "color": "red",
            "games": {
                "league-of-legends": {
                    "priority": 4,
                    "domain": "lol.jycsd.com",
                    "brand": "LoLGuide",
                    "sections": {
                        "champions": "英雄攻略 — 160+英雄出装/符文/对线",
                        "tier-lists": "Tier排名 — 各位置/版本最强英雄",
                        "jungle": "打野路线 — 清野路径/Gank时机",
                        "items": "装备分析 — 神话/传说装备选择",
                    },
                    "article_count": 200,
                },
                "fortnite": {
                    "priority": 5,
                    "domain": "fortnite.jycsd.com",
                    "brand": "FortGuide",
                    "article_count": 80,
                },
                "valorant": {
                    "priority": 6,
                    "domain": "valorant.jycsd.com",
                    "brand": "ValGuide",
                    "article_count": 70,
                },
                "cs2": {
                    "priority": 13,
                    "domain": "cs2.jycsd.com",
                    "brand": "CS2Guide",
                    "article_count": 50,
                },
                "apex-legends": {
                    "priority": 14,
                    "domain": "apex.jycsd.com",
                    "brand": "ApexGuide",
                    "article_count": 60,
                },
            },
        },
        "mobile-games": {
            "label": "手游",
            "color": "blue",
            "games": {
                "genshin-impact": {
                    "priority": 15,
                    "domain": "genshin.jycsd.com",
                    "brand": "TeyvatGuide",
                    "article_count": 100,
                },
                "honkai-star-rail": {
                    "priority": 16,
                    "domain": "hsr.jycsd.com",
                    "brand": "AstralGuide",
                    "article_count": 80,
                },
            },
        },
        "retro-classic": {
            "label": "怀旧/经典",
            "color": "purple",
            "games": {
                "pokemon": {
                    "priority": 17,
                    "domain": "pokemon.jycsd.com",
                    "brand": "PokeGuide",
                    "article_count": 100,
                },
                "zelda": {
                    "priority": 18,
                    "domain": "zelda.jycsd.com",
                    "brand": "HyruleGuide",
                    "article_count": 80,
                },
            },
        },
    },
}

ANIME_MATRIX = {
    "portal": {
        "name": "AnimeWiki Hub",
        "domain": "anime.jycsd.com",
        "brand": "AnimeWiki",
        "slogan": "Your Anime Encyclopedia",
        "desc": "Character databases, episode guides, and fan resources for popular anime series.",
    },
    "categories": {
        "shonen": {
            "label": "少年热血",
            "color": "orange",
            "series": {
                "dragon-ball": {
                    "priority": 1,
                    "domain": "dragonball.jycsd.com",
                    "brand": "DragonBallWiki",
                    "article_count": 120,
                },
                "one-piece": {
                    "priority": 2,
                    "domain": "onepiece.jycsd.com",
                    "brand": "OnePieceWiki",
                    "article_count": 150,
                },
                "naruto": {
                    "priority": 3,
                    "domain": "naruto.jycsd.com",
                    "brand": "NarutoWiki",
                    "article_count": 120,
                },
                "demon-slayer": {
                    "priority": 4,
                    "domain": "demonslayer.jycsd.com",
                    "brand": "DemonSlayerWiki",
                    "article_count": 80,
                },
                "jujutsu-kaisen": {
                    "priority": 5,
                    "domain": "jujutsukaisen.jycsd.com",
                    "brand": "JJKWiki",
                    "article_count": 80,
                },
                "attack-on-titan": {
                    "priority": 6,
                    "domain": "aot.jycsd.com",
                    "brand": "AOTWiki",
                    "article_count": 80,
                },
                "my-hero-academia": {
                    "priority": 7,
                    "domain": "mha.jycsd.com",
                    "brand": "MHAWiki",
                    "article_count": 70,
                },
            },
        },
        "current-hits": {
            "label": "当季热门",
            "color": "pink",
            "series": {
                "solo-leveling": {
                    "priority": 8,
                    "domain": "sololeveling.jycsd.com",
                    "brand": "SoloLevelingWiki",
                    "article_count": 50,
                },
                "frieren": {
                    "priority": 9,
                    "domain": "frieren.jycsd.com",
                    "brand": "FrierenWiki",
                    "article_count": 50,
                },
                "chainsaw-man": {
                    "priority": 10,
                    "domain": "chainsawman.jycsd.com",
                    "brand": "ChainsawManWiki",
                    "article_count": 60,
                },
            },
        },
        "classics": {
            "label": "经典名作",
            "color": "indigo",
            "series": {
                "death-note": {"priority": 11, "domain": "deathnote.jycsd.com", "brand": "DeathNoteWiki", "article_count": 40},
                "fullmetal-alchemist": {"priority": 12, "domain": "fma.jycsd.com", "brand": "FMAWiki", "article_count": 50},
                "evangelion": {"priority": 13, "domain": "eva.jycsd.com", "brand": "EvaWiki", "article_count": 40},
                "cowboy-bebop": {"priority": 14, "domain": "bebop.jycsd.com", "brand": "BebopWiki", "article_count": 30},
            },
        },
    },
}

# Build order: Phase 1 first (tonight), Phase 2-3 follow
BUILD_ORDER = [
    # PHASE 1 — Tonight
    "minecraft",       # 沙盒/生存 #1
    # PHASE 2 — Week 1
    "elden-ring",      # 开放世界 #1
    "gta-6",           # 开放世界 #2 (发售前预热)
    "league-of-legends",  # 电竞 #1
    # PHASE 3 — Week 2
    "fortnite",        # 联机 #1
    "valorant",        # 联机 #2
    "hogwarts-legacy", # 开放世界 #3
    # PHASE 4+ — 后续铺量
    "terraria", "palworld", "baldurs-gate-3", "cyberpunk-2077",
    "valheim", "cs2", "apex-legends", "genshin-impact",
    "honkai-star-rail", "pokemon", "zelda",
]

TOTAL_GAME_SITES = 18
TOTAL_ANIME_SITES = 14
TOTAL_ARTICLES_ESTIMATE = 1500  # across first 4 sites

# === 设计参考（对标头部游戏攻略站） ===
DESIGN_REFERENCE = {
    "对标站点": {
        "minecraft.wiki": "方块像素风，绿色+棕色，卡片网格首页，按生物/方块/机制分类",
        "fextralife.com": "暗色主题，左导航+右内容，RPG/Soulslike专精，Infobox数据卡",
        "bg3.wiki": "独立Wiki标杆，极简干净，零广告体验，深紫+金色",
        "game8.co": "日系亮色，大图Hero，按游戏分Tab，移动端优先",
        "icy-veins.com": "角色Build为主，蓝+白，详细数据表，职业分类导航",
    },
    "设计原则": {
        "配色": "暗色背景（#1a1a2e或#0d1117）+ 游戏主题强调色",
        "布局": "Hero大图 → 快速导航卡片 → 最新攻略列表 → 分类索引",
        "文章模板": "统计卡片（右浮动）+ 简介 + 详细内容 + 图片集 + 关联链接",
        "图片类型": "游戏截图/物品渲染/角色立绘/信息图表",
        "图片尺寸": "Hero 1200x600, 卡片缩略图 400x300, 内容插图 800x450",
        "导航": "顶部固定导航栏 + 侧边分类树 + 面包屑",
        "移动端": "卡片堆叠，导航折叠为汉堡菜单",
        "页面类型": ["首页门户", "分类列表页", "文章详情页", "搜索页", "关于/联系页"],
    },
    "图片获取策略": {
        "官方媒体包": "press kits, fan kits — 免费编辑使用",
        "游戏内截图": "fair use — 攻略评测用途合法",
        "社区Wiki": "注明来源可引用 — CC BY-SA协议",
        "禁止": "同人图/Pixiv/DeviantArt（版权风险）, 官方周边商品图（商标风险）",
    },
}

# === 站点模板（每个游戏站复用） ===
SITE_TEMPLATE = {
    "files": [
        "index.html",          # 首页门户
        "about.html",          # 关于本站
        "contact.html",        # 联系方式
        "robots.txt",          # SEO
        "sitemap.xml",         # 站点地图
        "ads.txt",             # AdSense
    ],
    "folders": {
        "guides/": "攻略文章目录",
        "characters/": "角色/生物图鉴目录",
        "items/": "物品/装备目录（如适用）",
        "builds/": "角色Build/配装目录（如适用）",
    },
    "每站文章数": "60-200篇，取决于游戏深度",
    "单篇文章字数": "800-1500字 + 3-5张图",
}

if __name__ == "__main__":
    print(f"Game sites planned: {TOTAL_GAME_SITES}")
    print(f"Anime sites planned: {TOTAL_ANIME_SITES}")
    print(f"Phase 1 (tonight): Minecraft")
    print(f"Phase 2 (week 1): Elden Ring, GTA 6, LoL")
    print(f"Phase 3 (week 2): Fortnite, Valorant, Hogwarts Legacy")
