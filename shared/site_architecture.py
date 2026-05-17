"""
三类站点完整架构 + 域名方案 + 变现体系
基于境外头部站设计模式反向工程
"""

# ============================================================
# 域名方案（零额外成本 — 全部 jycsd.com 子域名）
# ============================================================
DOMAIN_PLAN = {
    "现有生活矩阵": {
        "main-site": "www.jycsd.com",
        "healthy": "healthy.jycsd.com",
        "pets": "pets.jycsd.com",
        "home": "home.jycsd.com",
        "finance": "finance.jycsd.com",
        "tech": "tech.jycsd.com",
        "travel": "travel.jycsd.com",
    },
    "游戏攻略矩阵": {
        "portal": "games.jycsd.com",
        "sites": {
            "minecraft": "minecraft.jycsd.com",
            "elden-ring": "eldenring.jycsd.com",
            "gta-6": "gta6.jycsd.com",
            "league-of-legends": "lol.jycsd.com",
            "fortnite": "fortnite.jycsd.com",
            "valorant": "valorant.jycsd.com",
            "hogwarts-legacy": "hogwartslegacy.jycsd.com",
            "terraria": "terraria.jycsd.com",
            "palworld": "palworld.jycsd.com",
            "baldurs-gate-3": "bg3.jycsd.com",
            "cyberpunk-2077": "cyberpunk2077.jycsd.com",
            "valheim": "valheim.jycsd.com",
            "cs2": "cs2.jycsd.com",
            "apex-legends": "apex.jycsd.com",
            "genshin-impact": "genshin.jycsd.com",
            "honkai-star-rail": "hsr.jycsd.com",
            "pokemon": "pokemon.jycsd.com",
            "zelda": "zelda.jycsd.com",
        },
    },
    "动漫百科矩阵": {
        "portal": "anime.jycsd.com",
        "sites": {
            "dragon-ball": "dragonball.jycsd.com",
            "one-piece": "onepiece.jycsd.com",
            "naruto": "naruto.jycsd.com",
            "demon-slayer": "demonslayer.jycsd.com",
            "jujutsu-kaisen": "jujutsukaisen.jycsd.com",
            "attack-on-titan": "aot.jycsd.com",
            "my-hero-academia": "mha.jycsd.com",
            "solo-leveling": "sololeveling.jycsd.com",
            "frieren": "frieren.jycsd.com",
            "chainsaw-man": "chainsawman.jycsd.com",
            "death-note": "deathnote.jycsd.com",
            "fullmetal-alchemist": "fma.jycsd.com",
            "evangelion": "eva.jycsd.com",
            "cowboy-bebop": "bebop.jycsd.com",
        },
    },
    "AI工具矩阵": {
        "portal": "tools.jycsd.com",
        "sites": {
            "ghibli-generator": "ghibli.jycsd.com",
            "prd-builder": "prdbuilder.jycsd.com",
            "ai-avatar": "avatar.jycsd.com",
            "anime-generator": "animegen.jycsd.com",
        },
    },
}

# ============================================================
# 第一类：游戏攻略站 架构与模板
# 对标 Fextralife + Icy Veins
# ============================================================
GAME_GUIDE_TEMPLATE = {
    "design_system": {
        "theme": "dark",
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_card": "#1a1f2e",
        "text_primary": "#e6edf3",
        "text_secondary": "#8b949e",
        "accent": "per-game (Minecraft=#4ade80, EldenRing=#fbbf24, LoL=#3b82f6)",
        "font_display": "'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "font_size_body": "16px",
        "line_height": "1.6",
    },
    "page_types": {
        "homepage": {
            "sections": [
                "hero_search",       # 大图Hero + 搜索框（最重要的导航入口）
                "quick_nav_cards",   # 6宫格快速入口卡片（Boss/角色/物品/任务/Build/新手）
                "latest_guides",     # 最新攻略列表（带日期+缩略图）
                "hot_topics",        # 当前版本热门话题（Tier列表/版本更新）
                "category_index",    # 按分类索引（见下方分类体系）
                "newsletter_cta",    # 订阅CTA（收集邮箱）
            ],
        },
        "guide_detail": {
            "sections": [
                "breadcrumb",        # 面包屑导航
                "infobox",           # 右浮动数据卡片（Boss属性/物品属性/角色数据）
                "intro",             # 简介段落
                "toc",               # 左侧固定目录（桌面端）
                "content_blocks",    # 正文区：段落+图片+数据表格+提示框
                "related_guides",    # 关联攻略卡片
                "comments_section",  # 评论区（可选）
            ],
            "infobox_fields": {      # 每个实体类型的数据卡字段
                "boss": ["name", "image", "location", "hp", "weakness", "drops", "recommended_level"],
                "item": ["name", "image", "type", "rarity", "stats", "how_to_get", "crafting_use"],
                "character": ["name", "image", "role", "skills", "best_build", "tier"],
            },
        },
        "category_listing": {
            "sections": [
                "category_header",   # 分类标题+描述
                "filter_bar",        # 排序/筛选（最新/最热/难度等）
                "article_grid",      # 3列卡片网格（缩略图+标题+摘要+标签）
                "pagination",        # 分页
            ],
        },
        "search": {
            "sections": [
                "search_input",      # 大搜索框
                "results_grid",      # 结果卡片
                "no_results",        # 无结果引导
            ],
        },
    },
    "category_system": {  # 每款游戏的统一分类体系
        "minecraft": [
            {"slug": "crafting", "name": "Crafting Recipes", "icon": "crafting-table"},
            {"slug": "mobs", "name": "Mobs Guide", "icon": "creeper"},
            {"slug": "building", "name": "Building Ideas", "icon": "bricks"},
            {"slug": "redstone", "name": "Redstone Tech", "icon": "redstone"},
            {"slug": "enchanting", "name": "Enchanting & Potions", "icon": "potion"},
            {"slug": "biomes", "name": "Biomes Explorer", "icon": "globe"},
        ],
        "elden-ring": [
            {"slug": "bosses", "name": "Boss Guides", "icon": "skull"},
            {"slug": "builds", "name": "Character Builds", "icon": "sword"},
            {"slug": "weapons", "name": "Weapons & Armor", "icon": "shield"},
            {"slug": "quests", "name": "NPC Quests", "icon": "scroll"},
            {"slug": "locations", "name": "Map & Locations", "icon": "map"},
            {"slug": "spells", "name": "Spells & Incantations", "icon": "sparkles"},
        ],
    },
    "image_strategy": {
        "types": ["游戏截图", "物品渲染图", "BOSS/角色立绘", "地图标注图", "数据对比表"],
        "sources": [
            "官方Press Kit（免费编辑使用权）",
            "游戏内截图（Fair Use — 攻略评测用途）",
            "社区Wiki共享资源（CC BY-SA）",
        ],
        "dimensions": {
            "hero": "1200x600",
            "card_thumb": "400x300",
            "content_illustration": "800x450",
            "infobox_portrait": "300x400",
        },
    },
}

# ============================================================
# 第二类：动漫角色站 架构与模板
# 对标 MyAnimeList + Fandom Anime Wiki
# ============================================================
ANIME_WIKI_TEMPLATE = {
    "design_system": {
        "theme": "dark",
        "bg_primary": "#0a0a1a",
        "bg_secondary": "#12122a",
        "bg_card": "#1a1a3e",
        "text_primary": "#f0f0ff",
        "text_secondary": "#8888aa",
        "accent": "per-series (龙珠=#ff6b35, 海贼王=#ffd700, 火影=#ff6b35, 鬼灭=#ff4081)",
        "font_display": "'Poppins', sans-serif",
        "font_body": "'Noto Sans', sans-serif",
        "font_jp": "'Noto Sans JP', sans-serif",  # 日文角色名
        "font_size_body": "16px",
    },
    "page_types": {
        "homepage": {
            "sections": [
                "hero_banner",       # 大图Hero（角色群像或主视觉）
                "featured_character", # 精选角色卡片（大卡片+信息）
                "character_grid",    # 角色卡片网格（头像+名字+简短描述）
                "latest_episodes",   # 最新剧集/章节
                "popular_ranking",   # 人气角色排行
                "category_tags",     # 标签云：种族/能力/组织/声优
            ],
        },
        "character_detail": {
            "sections": [
                "breadcrumb",
                "character_header",  # 角色名(日/英) + 大图 + 一句话描述
                "infobox",           # 右浮动数据卡（见下方字段）
                "appearance",        # 外观描述
                "personality",       # 性格特点
                "backstory",         # 背景故事
                "abilities",         # 能力/技能列表（带等级/描述）
                "relationships",     # 关系图谱（与其他角色）
                "trivia",            # 冷知识
                "gallery",           # 图集（官方设定图/动画截图）
                "voice_actors",      # 声优表（日/英）
            ],
            "infobox_fields": {
                "standard": [
                    "name_jp", "name_en", "name_romaji",
                    "image", "series", "first_appearance",
                    "race", "affiliation", "occupation",
                    "age", "birthday", "height", "blood_type",
                    "voice_actor_jp", "voice_actor_en",
                ],
            },
        },
        "episode_guide": {
            "sections": [
                "season_selector",   # 季度选择器
                "episode_list",      # 剧集列表（编号+标题+截图+简介）
                "arc_markers",       # 篇章标记
            ],
        },
    },
    "image_strategy": {
        "types": ["角色立绘", "动画截图", "官方设定图", "关系图谱", "声优照片"],
        "sources": [
            "官方角色图（Press Kit / 官网素材）",
            "动画截图（Fair Use — 评论/百科用途）",
            "MyAnimeList / AniList API 关联图",
        ],
        "dimensions": {
            "hero": "1200x500",
            "character_card": "300x400",
            "infobox_portrait": "300x450",
            "gallery_thumb": "200x200",
        },
    },
}

# ============================================================
# 第三类：AI工具站 架构与模板
# 对标 良辰美吉卜力生成器 + AI工具SaaS站
# ============================================================
AI_TOOL_TEMPLATE = {
    "design_system": {
        "theme": "dark",
        "bg_primary": "#0c0c0c",
        "bg_secondary": "#1a1a1a",
        "bg_card": "#242424",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "gradient (purple→pink 或 cyan→blue)",
        "font_display": "'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "font_size_body": "16px",
    },
    "page_types": {
        "landing": {
            "sections": [
                "hero_demo",         # Hero区嵌入实时试用（输入→生成→展示）
                "social_proof",      # 用户数/生成量/评分 数字展示
                "how_it_works",      # 三步说明：上传→处理→下载
                "example_gallery",   # 效果展示画廊（Before/After或风格对比）
                "features_bento",    # Bento网格展示功能（风格迁移/高清放大/批量处理）
                "use_cases",         # 使用场景卡片（设计师/营销/开发者/动漫粉）
                "pricing",           # 定价卡片（见变现体系）
                "testimonials",      # 用户评价
                "faq",               # 常见问题
                "final_cta",         # 最终行动号召
            ],
        },
        "pricing_page": {
            "sections": [
                "plan_comparison",   # 三栏定价对比（Free/Pro/Unlimited）
                "feature_matrix",    # 功能详细对比表
                "faq_pricing",       # 价格相关FAQ
            ],
            "tiers": {
                "free": {"name": "Free", "price": 0, "generations": "5/day", "quality": "SD", "watermark": True},
                "pro": {"name": "Pro", "price": 9.99, "generations": "200/month", "quality": "HD", "watermark": False},
                "unlimited": {"name": "Unlimited", "price": 29.99, "generations": "unlimited", "quality": "4K", "watermark": False, "commercial_use": True},
            },
        },
        "tool_interface": {
            "sections": [
                "prompt_input",      # 提示词输入区
                "style_selector",    # 风格选择器
                "reference_upload",  # 参考图上传
                "generation_output", # 生成结果展示
                "download_options",  # 下载选项（带水印/高清/商业授权）
                "history",           # 生成历史
            ],
        },
    },
    "monetization": {
        "model": "freemium + credit + subscription",
        "free_tier": "每日5次生成，带水印SD画质",
        "pro_tier": "$9.99/月，200次/月，HD无水印",
        "unlimited_tier": "$29.99/月，无限次数，4K+商业授权",
        "credit_packs": "$4.99=50次, $19.99=250次, $49.99=750次",
    },
}

# ============================================================
# 变现体系（三类站点通用三层模型）
# ============================================================
MONETIZATION_SYSTEM = {
    "tier_1_free": {
        "name": "流量变现层",
        "applicable": "所有内容站",
        "methods": [
            "Google AdSense — 页面内嵌广告位（每页2-3个）",
            "Amazon Associates — 游戏外设/手办/周边链接分成",
            "广告联盟 — Ezoic/Mediavine（流量达标后升级）",
        ],
        "ad_placement": [
            "文章顶部（标题下） — 728x90 Leaderboard",
            "文章中部 — 300x250 Rectangle",
            "侧边栏 — 300x600 Skyscraper",
            "文章底部 — 728x90",
        ],
    },
    "tier_2_tools": {
        "name": "工具付费层",
        "applicable": "游戏站（配装计算器/攻略PDF）+ 动漫站（角色关系图/壁纸包）+ 工具站（AI生图）",
        "methods": [
            "游戏攻略PDF打包 — $2.99-$4.99/份",
            "角色Build计算器Pro版 — $4.99/月",
            "AI头像/动漫风格生成 — $0.99-$9.99/次或订阅",
            "独家攻略/隐藏内容解锁 — $1.99/篇",
            "PRD模板/工具 — $9.99/套",
        ],
    },
    "tier_3_membership": {
        "name": "会员复购层",
        "applicable": "流量>1万/月的站点",
        "methods": [
            "去广告体验 — $2.99/月",
            "独家攻略提前看 — $4.99/月",
            "Discord私密社群 — $4.99/月",
            "月度攻略合集邮件 — 免费→引导付费",
        ],
    },
    "revenue_estimate": {
        "小型站(<1万PV/月)": "AdSense: $50-200/月 + 工具: $100-500/月",
        "中型站(1-10万PV/月)": "AdSense: $500-2000/月 + 联盟: $200-500/月 + 工具: $500-2000/月",
        "大型站(>10万PV/月)": "AdSense: $2000-10000/月 + 联盟: $500-2000/月 + 工具+会员: $2000-10000/月",
    },
}

# ============================================================
# 建站优先级
# ============================================================
BUILD_PRIORITY = {
    "phase_1_tonight": ["minecraft"],
    "phase_2_this_week": ["elden-ring", "gta-6", "league-of-legends", "dragon-ball"],
    "phase_3_next_week": ["fortnite", "valorant", "one-piece", "naruto", "ghibli-generator"],
    "phase_4_ongoing": ["remaining 18 game + 10 anime + 3 tool sites"],
}

if __name__ == "__main__":
    game_count = len(DOMAIN_PLAN["游戏攻略矩阵"]["sites"])
    anime_count = len(DOMAIN_PLAN["动漫百科矩阵"]["sites"])
    tool_count = len(DOMAIN_PLAN["AI工具矩阵"]["sites"])
    existing = len(DOMAIN_PLAN["现有生活矩阵"]) - 1  # minus portal
    print(f"总站点规划: 现有{existing} + 游戏{game_count} + 动漫{anime_count} + 工具{tool_count} = {existing+game_count+anime_count+tool_count}")
    print(f"域名成本: ¥0 (全部 jycsd.com 子域名)")
    print(f"Cloudflare Pages项目: {existing+game_count+anime_count+tool_count+3}个(含3个门户)")
