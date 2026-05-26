# 渣哥独立项目：Demon Slayer Wiki 站

## 项目概述
从零搭建 demon-slayer-site（鬼灭之刃Wiki），全流程独立完成，交付标准：审计0 ERROR + 图片100%豆包验证通过。

## 项目范围

### 站点定位
- 品牌名：Demon Slayer Wiki
- 域名：demonslayer.jycsd.com
- 风格：深色底（写实/暗黑系，参考 eldenring-site），accent 色用 #ff6b6b（日轮刀红）
- 受众：欧美动漫迷，18-30岁

### 内容结构
```
demon-slayer-site/
├── index.html              # 首页：角色轮播 + 新闻卡片 + 分类导航
├── characters/             # 角色指南（每人一页，共45人）
│   ├── index.html          # 角色索引页
│   │
│   │   # === 主角团 (6人) ===
│   ├── tanjiro-kamado.html
│   ├── nezuko-kamado.html
│   ├── zenitsu-agatsuma.html
│   ├── inosuke-hashibira.html
│   ├── genya-shinazugawa.html
│   ├── kanao-tsuyuri.html
│   │
│   │   # === 九柱 Hashira (9人) ===
│   ├── giyu-tomioka.html
│   ├── shinobu-kocho.html
│   ├── kyojuro-rengoku.html
│   ├── tengen-uzui.html
│   ├── mitsuri-kanroji.html
│   ├── muichiro-tokito.html
│   ├── gyomei-himejima.html
│   ├── sanemi-shinazugawa.html
│   ├── obanai-iguro.html
│   │
│   │   # === 退役/前任柱 (3人) ===
│   ├── kanae-kocho.html
│   ├── jigoro-kuwajima.html
│   ├── shinjuro-rengoku.html
│   │
│   │   # === 鬼舞辻无惨 + 十二鬼月上弦 (10人) ===
│   ├── muzan-kibutsuji.html
│   ├── kokushibo.html
│   ├── doma.html
│   ├── akaza.html
│   ├── hantengu.html
│   ├── gyokko.html
│   ├── daki.html
│   ├── gyutaro.html
│   ├── kaigaku.html
│   ├── nakime.html
│   │
│   │   # === 十二鬼月下弦 (3人) ===
│   ├── enmu.html
│   ├── rui.html
│   ├── kyogai.html
│   │
│   │   # === 鬼杀队相关 (7人) ===
│   ├── kagaya-ubuyashiki.html
│   ├── sakonji-urokodaki.html
│   ├── sabito.html
│   ├── makomo.html
│   ├── aoi-kanzaki.html
│   ├── hotaru-haganezuka.html
│   ├── kozo-kanamori.html
│   │
│   │   # === 鬼阵营其他 (3人) ===
│   ├── tamayo.html
│   ├── yushiro.html
│   ├── susamaru.html
│   │
│   │   # === 宇髄天元的三位妻子 (3人) ===
│   ├── suma.html
│   ├── makio.html
│   ├── hinatsuru.html
│   │
│   │   # === 传奇人物 (1人) ===
│   └── yoriichi-tsugikuni.html
├── breathing-styles/       # 呼吸法指南（共14种）
│   ├── index.html
│   ├── water-breathing.html
│   ├── flame-breathing.html
│   ├── thunder-breathing.html
│   ├── wind-breathing.html
│   ├── stone-breathing.html
│   ├── insect-breathing.html
│   ├── love-breathing.html
│   ├── serpent-breathing.html
│   ├── mist-breathing.html
│   ├── sun-breathing.html
│   ├── moon-breathing.html
│   ├── flower-breathing.html
│   ├── sound-breathing.html
│   └── beast-breathing.html
├── arcs/                   # 篇章指南（共12篇）
│   ├── index.html
│   ├── final-selection.html
│   ├── asakusa-arc.html
│   ├── tsuzumi-mansion.html
│   ├── mount-natagumo.html
│   ├── rehabilitation-training.html
│   ├── mugen-train.html
│   ├── entertainment-district.html
│   ├── swordsmith-village.html
│   ├── hashira-training.html
│   ├── final-battle-infinity-castle.html
│   └── final-battle-sunrise-countdown.html
├── blood-demon-arts/       # 血鬼术指南（共10篇）
│   ├── index.html
│   ├── cryokinesis.html
│   ├── dream-manipulation.html
│   ├── thread-manipulation.html
│   ├── spatial-warp.html
│   ├── biokinesis.html
│   ├── emotion-sensing.html
│   ├── poison-blood.html
│   ├── flesh-manipulation.html
│   └── electrokinesis.html
├── game-guides/            # 火之神血风谭攻略（共12篇，每日更新源）
│   ├── index.html
│   ├── hinokami-chronicles-tier-list.html
│   ├── tanjiro-combo-guide.html
│   ├── nezuko-support-guide.html
│   ├── giyu-water-breathing-combos.html
│   ├── rengoku-flame-breathing-guide.html
│   ├── akaza-boss-fight-strategy.html
│   ├── versus-mode-tips.html
│   ├── how-to-unlock-all-characters.html
│   ├── best-skills-to-upgrade.html
│   ├── story-mode-walkthrough.html
│   ├── online-rank-tips.html
│   └── sweep-the-board-guide.html
├── organizations/          # 组织介绍（2篇）
│   ├── demon-slayer-corps.html
│   └── twelve-kizuki.html
├── weapons/                # 日轮刀武器指南（共7篇）
│   ├── index.html
│   ├── nichirin-blades.html
│   ├── sword-colors.html
│   ├── forging-process.html
│   ├── hashira-blades.html
│   ├── ancient-blades.html
│   └── warding-masks.html
├── blog/                   # 博客（初始为0，daily_articles自动生成）
├── images/                 # 角色PNG + 文章配图
├── about.html
├── contact.html
├── privacy-policy.html
├── cookie-policy.html
├── terms.html
├── robots.txt
├── sitemap.xml
└── ads.txt
```

## 执行步骤

### 第1步：角色资料收集
对上述45个角色，每个收集：
- 角色英文全名
- 简短描述（2-3句，英文）
- 所属组织（Demon Slayer Corps / Twelve Kizuki / 独立）
- 呼吸法/血鬼术
- 声优（日/英）
- 首次登场篇章

数据源：Kimetsu no Yaiba Wiki (kimetsu-no-yaiba.fandom.com)

### 第2步：图片下载 + 豆包验证
对每个角色下载2-3张PNG渲染图：
```bash
python shared/download_images.py --site demon-slayer-site --character <name>
```
- 每张图必须豆包 YES 才存盘
- 命名：`tanjiro-kamado.png`, `tanjiro-kamado_2.png`, `tanjiro-kamado_3.png`
- 不通过的重试最多9次
- 全部失败的角色记入 failed_images.json

### 第3步：站点渲染
```bash
python shared/render_game_site.py --site demon-slayer-site
```
如果 render_game_site.py 不支持新站，手动创建HTML（用 eldenring-site 作为模板，调整配色和内容）。

### 第4步：SEO + 合规配置
- robots.txt: Allow all, Sitemap指向 sitemap.xml
- sitemap.xml: 列出所有页面
- ads.txt: `google.com, pub-2595917642864488, DIRECT, f08c47fec0942fa0`
- 每个页面有完整的 meta（og:title, og:description, og:image, og:type, og:locale, og:site_name）
- 每个页面有 JSON-LD Schema
- 每个页面有 google-adsense-account meta
- Footer 下拉菜单含 Myers Media + Main Site + 所有兄弟站链接
- 所有页面含 `<blockquote>` 至少1个

### 第5步：注册到系统配置

#### 5a. 添加到 site_config.json
在 `shared/site_config.json` 的 `sites` 数组中添加：
```json
{
  "dir": "demon-slayer-site",
  "cf_project": "demonslayer-jycsd",
  "domain": "demonslayer.jycsd.com",
  "production_branch": "master"
}
```

#### 5b. 添加到 daily_articles.py
在 `shared/daily_articles.py` 的 GAME_SITES 列表中添加 `"demon-slayer-site"`，确保每日自动生成。

#### 5c. 创建 CF Pages 项目
在 Cloudflare Dashboard 创建新 Pages 项目 `demonslayer-jycsd`，等部署时再上传。或者部署时用 `wrangler pages project create demonslayer-jycsd`。

### 第6步：自检验收
```bash
python shared/pre_commit_audit.py --site demon-slayer-site
```
必须 0 ERROR。有错就修，修到过为止。

### 第6步：交付
- 提交所有文件到 git
- 输出完成报告

## 铁律（必须遵守）
1. **图片必须豆包验证** — 每张图豆包YES才存，不通过的不存
2. **内容禁止编造** — 角色描述、呼吸法说明必须来自真实资料源
3. **页面禁止出现中国身份** — 江阴/车速递/CheSuDi/China 等绝不出现
4. **禁止emoji** — 所有页面内容零emoji
5. **广告位规范** — 手动广告为主，只用谷歌标准尺寸
6. **审计0 ERROR才交付** — 不过审计不叫完成

## 交付物
```
=== Demon Slayer 站交付报告 ===

角色页面: 45/45（主角6 + 九柱9 + 退役柱3 + 上弦10 + 下弦3 + 鬼杀队7 + 鬼阵营3 + 妻子3 + 传奇1）
呼吸法页面: 14/14
篇章页面: 12/12
血鬼术页面: 10/10
组织页面: 2/2
游戏攻略页面: 12/12
总页面: 95+
图片: X张（全部豆包验证通过）
审计: 0 ERROR
失败图片: Y张（需人工找图，清单见 failed_images.json）
每日更新: 攻略板块已接入 daily_articles.py 生成管线

总耗时: X小时
```

## 每日更新整合

游戏攻略板块（game-guides/）建好后，`daily_articles.py` 每轮为 demon-slayer-site 生成1篇角色攻略，内容方向：
- 角色对战策略（counter picks, 连招技巧）
- Boss战攻略更新
- 版本更新/平衡性调整解读
- 新手入门指南变体

## 全站推广计划

Demon Slayer 是攻略板块模板站。验收通过后，渣哥按此模式为以下游戏/动漫站逐一添加攻略板块：

| 站点 | 攻略类型 | 攻略板块名称 |
|------|---------|-------------|
| demon-slayer-site | 火之神血风谭 角色/连招/Boss | game-guides/（模板站）|
| dragonball-site | Sparking Zero / FighterZ 角色攻略 | game-guides/ |
| naruto-site | Storm Connections 角色连招 | game-guides/ |
| onepiece-site | Pirate Warriors 角色攻略 | game-guides/ |
| eldenring-site | Boss攻略 / 武器Build / 地图 | guides/（已有目录结构）|
| minecraft-site | 合成配方 / 红石技巧 / 建筑 | guides/ |
| lol-site | 英雄counter / 对线 / 出装 | guides/ |
| fortnite-site | 武器搭配 / 建筑技巧 / 赛季 | guides/ |
| valorant-site | Agent技能 / 地图点位 / 枪法 | guides/ |
| bleach-site | Rebirth of Souls 角色攻略 | game-guides/ |
| jjk-site | Cursed Clash 角色对战 | game-guides/ |
| aot-site | AOT 2 巨人讨伐 / 装备升级 | game-guides/ |
| jojo-site | ASBR 角色连招 / 替身 | game-guides/ |
| hxh-site | Nen Impact 念能力对战 | game-guides/ |
| sao-site | Fatal Bullet 武器Build | game-guides/ |
| tokyoghoul-site | Call to Exist 喰种对战 | game-guides/ |
| anime-site | 综合动漫游戏攻略 | game-guides/ |
| games-site | 多游戏攻略聚合 | guides/ |

**执行节奏**：Demon Slayer 先跑通 → daily_articles.py 确认每天能产出1篇攻略 → 批量复制到17站 → 每日每站1篇角色攻略 = 每天17篇新内容。

这样 Google 爬虫每天爬17站都有新内容，AdSense 曝光量翻倍。
