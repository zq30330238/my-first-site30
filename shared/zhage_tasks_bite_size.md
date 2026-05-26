# 渣哥任务 — Demon Slayer 站（分步执行，每步做完回复再发下一步）

## 你的任务：从零搭建 demon-slayer-site（鬼灭之刃Wiki）

每步完成后来报告，我验证通过后发下一步。不要一口气全做。

---

### 第1步：建站骨架
创建目录和首页，用 eldenring-site 风格（深色底+暗黑系）。

```
站点目录: d:\AI网站文件夹\demon-slayer-site\
风格参考: d:\AI网站文件夹\eldenring-site\
品牌色: #ff6b6b（日轮刀红）
```

创建文件:
- index.html（首页：Banner轮播+分类导航卡片）
- about.html, contact.html, privacy-policy.html, cookie-policy.html, terms.html
- robots.txt, sitemap.xml, ads.txt
- images/ 目录

验证: `ls d:\AI网站文件夹\demon-slayer-site\` 有8+个文件

---

### 第2步：角色资料收集
去 `https://kimetsu-no-yaiba.fandom.com` 收集45个角色资料。

每个角色查: 英文全名、简介(2-3句)、组织、呼吸法/血鬼术、声优(日/英)、首登场篇章

存到: `d:\AI网站文件夹\demon-slayer-site\character_data.json`

结构: `{"name": "tanjiro-kamado", "full_name": "Tanjiro Kamado", ...}`

角色清单: tanjiro-kamado, nezuko-kamado, zenitsu-agatsuma, inosuke-hashibira, genya-shinazugawa, kanao-tsuyuri, giyu-tomioka, shinobu-kocho, kyojuro-rengoku, tengen-uzui, mitsuri-kanroji, muichiro-tokito, gyomei-himejima, sanemi-shinazugawa, obanai-iguro, kanae-kocho, jigoro-kuwajima, shinjuro-rengoku, muzan-kibutsuji, kokushibo, doma, akaza, hantengu, gyokko, daki, gyutaro, kaigaku, nakime, enmu, rui, kyogai, kagaya-ubuyashiki, sakonji-urokodaki, sabito, makomo, aoi-kanzaki, hotaru-haganezuka, kozo-kanamori, tamayo, yushiro, susamaru, suma, makio, hinatsuru, yoriichi-tsugikuni

验证: `python -c "import json; d=json.load(open('d:/AI网站文件夹/demon-slayer-site/character_data.json')); print(len(d))"` 输出 45

---

### 第3步：角色图片下载
对第2步的45个角色，逐个下载图片:

```bash
cd "d:\AI网站文件夹"
python shared/download_images.py --site demon-slayer-site --character <角色名> --max-images 2
```

每个角色下2张图。豆包验证不过的重试最多9次。全部失败的记入 failed_images.json。

验证: `ls d:\AI网站文件夹\demon-slayer-site\images\ | wc -l` 至少60张

---

### 第4步：角色页面渲染
用 character_data.json 为45个角色各生成一个HTML页面，放到 `characters/` 目录。

模板参考: `d:\AI网站文件夹\eldenring-site\characters\`

每个页面必须含: 角色名、简介、组织、呼吸法/血鬼术、声优、首登场、至少2张图片、blockquote至少1个、完整meta+og标签、JSON-LD Schema

另外创建 `characters/index.html`（角色索引页，列出全部45人）

验证: `find d:\AI网站文件夹\demon-slayer-site\characters\ -name "*.html" | wc -l` 输出 46

---

### 第5步：内容板块页面
创建以下目录和页面，每个目录有 index.html 和子页面:

1. breathing-styles/ — 14种呼吸法（water, flame, thunder, wind, stone, insect, love, serpent, mist, sun, moon, flower, sound, beast）
2. arcs/ — 12个篇章（final-selection, asakusa-arc, tsuzumi-mansion, mount-natagumo, rehabilitation-training, mugen-train, entertainment-district, swordsmith-village, hashira-training, final-battle-infinity-castle, final-battle-sunrise-countdown）
3. blood-demon-arts/ — 10种血鬼术
4. organizations/ — 2个组织（demon-slayer-corps, twelve-kizuki）
5. weapons/ — 7篇武器指南（nichirin-blades, sword-colors, forging-process, hashira-blades, ancient-blades, warding-masks）
6. game-guides/ — 12篇火之神血风谭攻略

每个页面必须有: blockquote, meta/og标签, JSON-LD, AdSense广告位

验证: `find d:\AI网站文件夹\demon-slayer-site\ -name "*.html" | wc -l` 至少95个文件

---

### 第6步：审计验收
```bash
cd "d:\AI网站文件夹"
python shared/pre_commit_audit.py --site demon-slayer-site
```

必须0 ERROR。有错就修到过为止。

然后把 demon-slayer-site 加到 shared/site_config.json 和 shared/daily_articles.py。

验证: 审计输出 "Commit READY. 0 ERRORS"

---

铁律:
- 图片必须豆包验证YES才存
- 内容禁止编造，必须来自真实资料
- 页面禁止出现中国身份（江阴/车速递/CheSuDi/China）
- 禁止emoji
- Footer用下拉菜单，含兄弟站链接
