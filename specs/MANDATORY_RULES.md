# 新站建设强制性规定 (Mandatory New Site Construction Rules)

**效力**: 每条规定都是从实际Bug/事故/教训中提炼。违反任一条=重蹈覆辙。
**执行方式**: 每个新站从spec到部署的每个阶段，逐条对照执行，不跳过不降级。
**铁律**: 发现问题→立即停手→记录规则→再继续 (见 [[stop-record-then-continue]])

---

## 第零阶段: 项目启动前 (Pre-Project)

### P0.1 强制规则匹配
- [ ] 读取 `rule_index.json`，按任务类型(new_site)匹配所有相关规则
- [ ] 逐条Read确认约束，不查不动手
- [ ] 设计类任务动手前 `grep` 记忆目录查相关约束

### P0.2 Spec先行
- [ ] 新站必须先写完整spec文件 (`specs/<site-dir>.md`)
- [ ] Spec必须含: 基本信息+页面结构+分类设计+图片清单+内容大纲+实现步骤+验收标准
- [ ] Spec必须含质量与UX标准章节
- [ ] Spec必须含CTR/流量优化章节
- [ ] Spec经用户审阅批准后才能开工

### P0.2.1 页面结构强制对照 (Spec-Cross-Reference — 零容忍)
**绝不允许spec页面结构与同类型老站不一致。这是刚性规则，无例外。**

- [ ] Spec写页面结构前，先选一个同类型老站作为参照（内容站参照sub-healthy，游戏站参照naruto-site，动漫站参照aot-site）
- [ ] **逐文件对照**: 列出参照站所有HTML文件 → 新站spec必须包含对应文件，每少一个必须有明确理由写在spec里
- [ ] 强制包含的页面类型（内容站）:
  - 固定页: index.html / about.html / contact.html / privacy-policy.html / terms.html / cookie-policy.html
  - 列表页: **articles.html**（全部文章列表）、**category-*.html**（每个分类一个页面）
  - 文章页: article-N.html（每分类≥6篇）
  - 配置: robots.txt / ads.txt / sitemap.xml / favicon.ico
- [ ] **禁止在spec中写"无需单独HTML"** 来跳过参照站已有的页面类型 — 这等于故意制造死链
- [ ] 每个导航链接、每个按钮href、每个分类卡片链接 → 必须有对应的目标页面存在
- [ ] **验证**: spec批准前，跑 `ls <参照站>/*.html | wc -l` vs `grep '\.html' <新站spec> | wc -l` 确认数量匹配
- [ ] 教训来源: sub-career spec写"分类索引页无需单独HTML"，5个分类卡片成死链；View All指向不存在的articles.html，临时改sitemap凑合被强哥当场指出

### P0.2.2 配置值禁止凭空编造 (No Invention Rule)
**所有跨站共享的配置值必须从已有站点copy，不允许Agent随意发挥。**

- [ ] GA4 ID: 必须用 `G-GGNWR1X1GV`，从任一已有站点首页复制
- [ ] AdSense pub ID: 必须用 `ca-pub-2595917642864488`
- [ ] 品牌名: 必须用 `Myers Media`，创始人 `Jordan Myers`
- [ ] 联系邮箱: 必须用 `contact@jycsd.com`
- [ ] 写spec前，先打开参照站首页看一遍实际使用的配置值，照抄，不自己编
- [ ] 教训来源: sub-career被Agent编了个不存在的GA4 ID `G-H8JL6Z7K7Q`，GSC无法自动验证

### P0.2.3 新站必须第一时间注入 site_config.json (Config-First — 零容忍)
**spec批准后，第一件事不是写代码，是更新配置文件。json永远是唯一权威源。**

- [ ] **spec批准后立即在 `site_config.json` 加一条**: `{"dir":"<site-dir>","cf_project":"<project>","domain":"<domain>","production_branch":"master","category":"<content|game|anime|...>"}`
- [ ] **同时在 `site_templates.py` 的 `build_footer_links()` 的 `NAME_MAP` 加域名→显示名映射**
- [ ] **立即跑 `python shared/refresh_footer.py`** — 刷新所有现有站 footer，新站域名出现在全站下拉框
- [ ] **先改json再干别的** — 不在json里的站=不存在。禁止"先建站再加配置"
- [ ] 教训来源: 2026-05-29 footer链接列表硬编码在build_footer_links()里，与site_config.json独立维护，新建站容易漏更新。改为build_footer_links()从json动态读取+NAME_MAP映射，新建站只改两处(json+NAME_MAP)，不碰代码逻辑

### P0.3 先模版再批量
- [ ] 同类网站先做一个完整模版(首页+1篇完整文章+1个分类页)
- [ ] 用户验收通过后，再批量克隆到其他同类站
- [ ] 绝不一开始就同时铺量

### P0.4 单篇全量验证后再批量生成 (Single-Article Full Audit Before Batch)
- [ ] **生成第1篇文章后立即跑 pre_commit_audit.py** — 不等30篇全生成完
- [ ] 第1篇过审计后，人工读一遍确认: Auto Ads脚本/google-adsense-account meta/og:locale/ads.txt pub ID/图片路径/FAQ特异性/Schema完整性/HTML四标签
- [ ] **第1篇强制验证命令（逐条跑，不凭感觉）**:
  ```bash
  # 1. HTML四标签完整性
  grep -c '</head>\|<body\|</body>\|</html>' article-1.html
  # 2. 图片路径绝对（禁止../images/）
  grep -c '\.\.\/images\/' article-1.html  # expect 0
  # 3. 邮箱正确（禁止zq30338@gmail.com在页面中）
  grep -c 'zq30338\|@qq.com' article-1.html  # expect 0
  # 4. 无AI cliche
  grep -ci 'delve into\|in conclusion\|whether you.re a\|in today.s fast-paced' article-1.html  # expect 0
  # 5. 封面图URL可访问（非404）
  curl -s -o /dev/null -w "%{http_code}" <提取og:image URL>  # expect 200
  # 6. 审计
  python shared/pre_commit_audit.py --site <site_dir>  # expect 0 ERROR
  ```
- [ ] 第1篇确认0 ERROR后，才能用同一模板批量生成剩余29篇
- [ ] **严禁模板未经验证就批量生成** — 模板有遗漏=30篇文章全部有同样遗漏=三轮修复才到位
- [ ] 教训来源: sub-career站，Agent生成的模板缺Auto Ads/google-adsense-account/og:locale，30篇全部缺，D5.0自检才发现，来回修三轮
- [ ] 教训来源: sub-beauty站，第1篇未做逐条验证即批量30篇→5张banner全404、11篇缺</body>、email全错、../images/路径残留。P0.4走形式=30篇全带同样bug

### P0.5 生成完成≠站完成 — 立即跑审计
- [ ] 所有内容生成完毕后，立即跑 `pre_commit_audit.py`，只看本站ERROR
- [ ] **禁止在跑审计前说"站建完了"** — 审计0 ERROR才算建完
- [ ] 教训来源: sub-career站宣布"完成"后跑审计发现4类ERROR+5篇泛化FAQ+3对MD5重复

---

## 第一阶段: 模板设计 (Template Design)

### T1.1 禁止硬编码站点专属链接
- [ ] 模板中绝不硬编码分类链接(如 category-reviews/ev/buying)
- [ ] 所有导航项通过 SITE_CONFIG 按站配置，没有配置就不显示
- [ ] 导航栏只保留 Home/About/Contact 通用链接，其余按配置动态生成

### T1.2 模板输出即合规
- [ ] 模板必须在设计时就内嵌所有标准(blockquote+标题长度+广告位+Schema)
- [ ] 输出天然合规，审计只是走过场确认
- [ ] 审计只设两档: ERROR(block部署) 和 WARN(不block但有记录)
- [ ] 绝不以降级标准换取审计通过

### T1.3 Footer强制规范
- [ ] 所有站点footer互链统一用 `<select>` 下拉菜单 (3个: Network/Content Sites/Game & Anime Wikis)
- [ ] 禁止用 ul/li 纯链接 "Our Sites"
- [ ] 下拉菜单含所有在线站点，按类型分组
- [ ] Footer品牌: Myers Media，创始人 Jordan Myers

### T1.4 Logo与品牌
- [ ] Header/Footer品牌标识禁止用角色图片(每页都出现造成视觉疲劳)
- [ ] **GA4统一ID**: 全站一个GA4 `G-GGNWR1X1GV`，严禁用其他GA4 ID。不同GA4→GSC无法自动验证→每次手动加meta标签。教训: sub-career误用`G-H8JL6Z7K7Q`，GSC验证失败
- [ ] Logo用文字或抽象SVG图标
- [ ] **绝对禁止页面中出现任何中国身份标识**: 江阴/车速递/CheSuDi/Jiangyin/China/founded in China/JYCSD Network
- [ ] 对外品牌统一: Myers Media，创始人 Jordan Myers
- [ ] 联系邮箱: contact@jycsd.com — **所有页面Schema/页脚/联系信息统一使用，严禁zq30338@gmail.com或@qq.com出现**。验证: `grep -rn 'zq30338\|@qq.com' *.html` = 0
- [ ] 教训来源: sub-beauty 4个页面(contact/cookie/privacy/terms)的Organization Schema中email为zq30338@gmail.com，T1.4违规

### T1.5 广告位规范
- [ ] **纯自动广告模式**，禁止 `<ins class="adsbygoogle">` 和 `data-ad-slot` 手动广告位
- [ ] **禁止广告占位容器** — 禁止 `.ad-unit`/`.ad-label`/`.ad-placeholder` div、虚线框、假"Advertisement"文字
- [ ] 只需 `<script async src="adsbygoogle.js">` 一行，Google 自己决定位置和数量
- [ ] 广告不打断阅读流，不在首屏(viewpoint)堆叠
- [ ] 暗色底站点: 广告位用浅色卡片容器(`bg-gray-100 rounded`)包裹
- [ ] 教训来源: sub-career擅自加3个ad-unit占位div+CSS，老站全无此物，纯画蛇添足

### T1.6 图片视觉规范
- [ ] **图片上禁止任何阴影遮罩**: `bg-black/`, `bg-gradient-to-t`, `linear-gradient(rgba())`, `bg-black/50`等覆盖层
- [ ] 文字可读性用 `text-shadow: 0 2px 8px rgba(0,0,0,0.8)` 替代遮罩
- [ ] 大图大尺寸: 图片 `object-cover` 填满容器，宽高一致，禁用白色背景
- [ ] 文字在图片右侧: 横向flex卡片布局，整卡`<a>`可点击
- [ ] 竖版图片在横版容器中: `object-position` 需下移，优先用横版图
- [ ] **人物图片必须露头**: 含人脸/人物的banner/hero/卡片背景图，`background-position` 禁止用 `center`（默认居中裁切=头部截断）。必须偏向上方，人物肖像类 `50% 15%`，团队照 `50% 20-25%`，根据实际构图调整。教训: sub-career banner slide 2 女性肖像头部被截断，只剩下巴
- [ ] **Banner轮播图必须逐张用豆包验证**: 检查每张banner slide是否有面部/人物被裁切。不能用代码审计替代

### T1.7 正则与HTML处理
- [ ] **所有脚本中操作HTML的正则必须使用 `re.DOTALL`** — 不仅生成脚本，审计/验证/健康检查全部

### T1.8 首页Hero与内容区角色禁止重复（零容忍 — 2026-05-30新增）
**Hero轮播大图区与下方卡片网格用同一批角色=用户同一个角色看到两次=视觉重复=偷懒感。**

- [ ] Hero轮播（8张）和下方"Meet the Characters"卡片（前8张）必须使用**完全不同的角色**
- [ ] 角色优先级: 主角团/最受欢迎角色→Hero轮播，次要角色→卡片网格区
- [ ] 禁止同一角色图片同时出现在Hero和卡片区
- [ ] 验证: carousel img src集合 ∩ card grid img src集合 = 空集
- [ ] 教训来源: demonslayer-site，Hero 8角色(akaza/daki/doma/enmu/genya/giyu/gyomei/gyutaro)与卡片前8完全相同

### T1.9 禁止负margin覆盖内容区（零容忍 — 2026-05-30新增）
**`-mt-N` 负边距把文字/blockquote拉入banner区域=内容被遮挡=不可读。**

- [ ] 禁止在Hero/Banner之后的第一个内容区使用负margin (`-mt-*`)
- [ ] Banner和文字内容之间必须用正margin隔开（`mt-6` 或更大）
- [ ] 验证: 首页Hero后的blockquote/intro text在768px+视口下不被banner遮挡
- [ ] 教训来源: chinese-architecture-site，blockquote `-mt-6` 把"5000 years of cultural heritage"文字拉入hero图下方被遮挡

### T1.10 禁止符号占位符（零容忍 — 2026-05-30新增）
**`&#9670;` / `◆` / `●` 等纯符号占位=内容未完成=给用户半成品印象。**

- [ ] HTML最终产出中禁止任何纯符号占位符（`&#9670;`、`◆`、`●`、`★` 等）
- [ ] 用真实图片、真实文字或CSS图标替代
- [ ] 模板中不留占位符——每个元素在输出时必须有实际内容
- [ ] 教训来源: demonslayer-site privacy-policy/terms/cookie-policy 多页含 `&#9670;` diamond占位
- [ ] 禁止 `html.count('<img src=')` 等单行假设写法
- [ ] 正确写法: `re.findall(r'<img\s[^>]*src=', html, re.DOTALL)`
- [ ] 禁止生成多行 `<img>` 标签 — `<img>` 标签必须单行完整

---

## 第二阶段: 图片处理 (Image Pipeline)

### I2.1 下载/生成后必须压缩
- [ ] Seedream生成/Pexels下载/Unsplash下载的图片 → PIL压缩
- [ ] 参数: `max_width=1200, quality=85`，不压缩不上传
- [ ] WebP可作备选格式，JPEG为主

### I2.2 图片内容匹配强制验证（零容忍 — 2026-05-29升级）

**图片与文章内容不匹配=用户看到随机图=信任崩塌。这是系统性漏洞，不是小问题。**

- [ ] **每张文章配图必须经过豆包视觉API验证** — 确认图片内容与文章标题主题高度相关
- [ ] 验证prompt: `"这是文章的配图。文章标题是：「{title}」请判断：这张图片的内容是否与文章标题的主题高度相关？只回答'匹配'或'不匹配'。如果是不匹配，用一句话说明图片实际内容。"`
- [ ] 验证不通过 → 立即换关键词重搜Pexels（最多5次）→ 仍不通过 → 走ARK Seedream生成
- [ ] 豆包首次验证即识别错误群体时，SMART-SKIP: 跳过剩余Pexels重试直接走Seedream
- [ ] **每站部署前必须跑 `audit_image_content_match.py`** 生成 `image_mismatch_report.json`
- [ ] **pre_commit_audit.py 强制读取 image_mismatch_report.json** — 存在未修复mismatch=ERROR阻断部署
- [ ] **新站验收标准**: image_mismatch_report.json中该站所有文章status="match"或"fixed"，0 mismatch
- [ ] **禁止跳过视觉验证**: 豆包API不可用时暂停建站，不得以降级方案(随机图/default-og)替代
- [ ] 修复工具: `python shared/fix_mismatched_images.py <site_dir>` — Pexels→豆包验证→Seedream→压缩全管道
- [ ] **违反示例(2026-05-29)**: 14站702篇文章审计发现189+处图片与标题不匹配，career站102篇中69%不匹配(配图:山景→简历写作、沙漠→技术面试、日本街景→副业管理)。根因: picsum.photos随机图替代default-og.jpg，图片管道缺少视觉验证环节

### I2.3 模板图片去重
- [ ] about_hero.jpg等共享图每站独立生成，不用模板复制
- [ ] 跨站图片MD5去重检查
- [ ] 每个角色/条目至少2-3张不同图片

### I2.4 图片命名与路径
- [ ] 图片路径统一用 `/images/` 绝对路径，禁止 `../images/` 相对路径
- [ ] 文件名语义化: `tanjiro-kamado.jpg` 而非 `img001.jpg`

### I2.5 禁止外部图片URL（零容忍）
- [ ] **所有 `<img src>` 必须指向本地 `/images/` 目录**，禁止任何外部URL
- [ ] 禁止 `images.unsplash.com` / `source.unsplash.com` / `picsum.photos` 等外部图片源
- [ ] 图片必须先下载→豆包验证→PIL压缩→放入 `/images/` → 才能在HTML中引用
- [ ] AI生成文章时禁止让它"选一个Unsplash URL"——AI会编造假ID，100%不可信
- [ ] `batch_articles.py` / `create_articles.py` 等脚本：图片URL字段必须留空由 `collect_content_images.py` 后处理填充

---

## 第三阶段: 内容生成 (Content Generation)

### C3.1 AI输出安全清洗
- [ ] AI生成内容插入模板前必须清洗危险字符: `</head>`/`<body`/`</html>`/`<script`
- [ ] 使用 `html.escape()` 或正则替换
- [ ] quick_validate()强制检查 `</head>`/`<body>`/`</body>`/`</html>` 四个标签完整性

### I2.6 图片必须实际存在——禁止"空中楼阁"（零容忍）
- [ ] **每篇文章的配图必须实际下载到 `/images/` 目录**，确认文件存在且 HTTP 200
- [ ] AI生成HTML时禁止引用不存在的图片路径——先有图，后写HTML
- [ ] `batch_articles.py` / `create_articles.py` 等生成脚本必须: 图片下载完成 → 验证通过 → 才能写入 `<img src>`
- [ ] **禁止AI编造unsplash/pexels/picsum等任何外部URL** — AI的URL 100%幻觉，无一例外
- [ ] 检测方法: `pre_commit_audit.py` 扫描所有 `src="https?://"` 外部图片URL = ERROR
- [ ] **违反示例(2026-05-29 beauty站)**: 72篇文章配图全是AI编的假Unsplash URL，全部404；11篇文章缺`</body>`标签
- [ ] **禁止假图+禁止空引用+禁止假URL** — 三者任一出现=阻断部署

### I2.7 HTML结构完整性强制检查
- [ ] 每篇生成的文章必须包含四个标签: `</head>` + `<body`（或`<body>`） + `</body>` + `</html>`
- [ ] `quick_validate()` 强制四标签检查，缺任一=不通过
- [ ] 禁止无`</body>`结尾的文章入库——浏览器可容错但SEO扣分

### I2.8 禁止default-og.jpg出现在文章正文（零容忍 — 2026-05-29新增）
**default-og.jpg = Dragon Ball Z Logo。任何非龙珠站出现此图=弄虚作假。**

- [ ] **绝对禁止** `<img src="...default-og.jpg">` 出现在任何文章/分类页/卡片中
- [ ] default-og.jpg **只能**作为OG meta fallback（`<meta property="og:image">`），绝不可出现在可见页面内容
- [ ] 文章无图时必须下载真实图片，**禁止**用default-og.jpg顶替
- [ ] Agent生成HTML时**禁止使用default-og.jpg作为任何可见元素的src**
- [ ] `pre_commit_audit.py` 扫描 `src="...default-og.jpg"` → ERROR 阻断部署
- [ ] **违反示例(2026-05-29)**: healthy/pets/home/tech/travel/beauty/dailymedadvice/rightsdaily 共197处使用龙珠Z Logo作为文章封面/分类卡片图，严重欺诈

### I2.9 禁止MD5重复图片（零容忍 — 2026-05-29新增）
**同一张图片复制多份=不同文章共用一个封面=用户体验极差**

- [ ] 所有 `article-*.jpg` 必须MD5唯一——每篇文章独立配图
- [ ] `pre_commit_audit.py` 扫描images/目录MD5 → 发现重复=ERROR阻断
- [ ] 批量下载图片时必须用不同seed/随机参数确保唯一性
- [ ] **违反示例(2026-05-29)**: 19组48文件MD5重复（tech站同一张图用于article-1/44/45/46四篇文章，pets站三篇文章共图）

### I2.10 禁止Agent图片偷懒行为（零容忍 — 2026-05-29新增）
**Agent会钻一切空子，必须提前堵死所有可能的偷懒路径。**

- [ ] **禁止onerror fallback**: `<img onerror="this.src='default-og.jpg'">` — 下载失败必须重试，不得静默降级
- [ ] **禁止data: URI占位**: `<img src="data:image/svg+xml,...">` — 必须下载真实图片文件
- [ ] **禁止空src**: `<img src="">` 或 `<img>` 无src属性 — 必须指向真实文件
- [ ] **禁止CSS background-image外部URL**: `style="background-image:url(https://...)"` — 必须用本地图片
- [ ] **禁止跨站引用图片**: `src="../other-site/images/x.jpg"` — 每站只用自己images/目录
- [ ] **禁止图片zero-size**: width/height=0或文件<5KB的假图
- [ ] **禁止img标签完全缺失**: 文章页面必须有至少一张hero图
- [ ] `pre_commit_audit.py` 逐条拦截以上所有行为 → ERROR

### I2.11 default-og.jpg使用范围严格限制
**default-og.jpg唯一合法用途: 固定页面的OG meta fallback。**

- [ ] **合法**: `<meta property="og:image" content="...default-og.jpg">` — about/contact/privacy/terms等固定页
- [ ] **非法**: 文章页og:image必须指向文章专属图片（`/images/article-N.jpg`），不得用default-og.jpg
- [ ] **非法**: `<img src="...default-og.jpg">` 任何可见内容中
- [ ] **非法**: `<div style="background-image:url(...default-og.jpg)">` 
- [ ] **非法**: `<a href="...default-og.jpg">` 任何链接/引用中

---

## 第三阶段: 内容生成 (Content Generation)

### C3.1 AI输出安全清洗
- [ ] AI生成内容插入模板前必须清洗危险字符: `</head>`/`<body`/`</html>`/`<script`
- [ ] 使用 `html.escape()` 或正则替换
- [ ] quick_validate()强制检查 `</head>`/`<body>`/`</body>`/`</html>` 四个标签完整性

### C3.2 禁止凭空编造（零容忍，含AI幻觉）
- [ ] 所有事实性内容必须有真实数据源
- [ ] 不得编造统计数据/研究引用/专家言论/用户评价/案例细节
- [ ] 不确定的信息标注 "general advice" 而非 "research proves"
- [ ] **禁止AI编造任何URL/文件名/图片路径** — 所有文件引用必须基于实际存在的文件
- [ ] **禁止AI生成Unsplash/Pexels/Picsum等外部图片URL** — AI编的照片ID必然404
- [ ] 禁止AI cliché: "In this guide, we'll"/"Let's dive in"/"Moreover"/"In conclusion"/"whether you're a"/"delve into"/"in today's fast-paced world"

### C3.3 Agent委派规范（2026-05-29强化）
- [ ] 单次Agent内容生成≤5页，超标分section并行
- [ ] Agent prompt用禁止句式而非指导句式: "必须处理以下X个目录，缺一不可"
- [ ] 每个"如果没有X"必须跟"就用Y替代"，不给agent留"跳过=完成任务"的选项
- [ ] Agent prompt末尾必须包含验证命令(bash脚本)，期望值写死在命令里
- [ ] Agent返回done后必须数字验证: `grep -c 'article-card' index.html` 输出数字才信
- [ ] **禁止Agent使用default-og.jpg** — Agent生成任何HTML时，`img src`必须指向实际图片路径，无图则下载，绝不用default-og.jpg占位
- [ ] **禁止Agent生成重复图片** — 每篇文章配独立图片，不同seed/不同URL，不得复制同一图片
- [ ] **Agent prompt必须包含**: "每个img标签的src必须指向唯一的/images/路径。禁止使用default-og.jpg。禁止多个文件引用同一图片。"

### C3.4 主题避重
- [ ] 生成文章前明确指定主题列表，防止不同站点内容重叠
- [ ] 每站每分类≥6篇，每篇≥1200字(内容站)/≥500字(游戏动漫)

### C3.6 Hub引导页必须有实质内容（零容忍 — 2026-05-30新增）
**Anime/Game总站的guides子目录页是用户进入完整Wiki的入口。空页面="Content is being curated"=跳出率100%。**

- [ ] 每个 `/guides/<ip>/index.html` 必须包含:
  - Top Characters卡片网格（≥8张，图片从对应Wiki站引用）
  - Browse by Category分类链接区（3-5个分类）
  - "Visit Full Wiki →"按钮链接到独立Wiki站
- [ ] 禁止空占位页面。内容未准备好=页面不存在，不能上线
- [ ] 验证: `grep -c 'Top Characters' guides/*/index.html` ≥ 6（每个guide页都是完整hub）
- [ ] 教训来源: anime-site/guides/jjk/ 和 demonslayer/ 只有占位文字，用户报告"空的"

### C3.7 首页文章卡片数全站一致（2026-05-30新增）
**同一类型站点的首页文章卡片数必须一致。A站12篇B站10篇=B站看起来内容少=用户信任降。**

- [ ] 同类型参照站首页卡片数为基准（如内容站参照healthy=12篇）
- [ ] 新站首页卡片数不得低于基准站
- [ ] 验证: `grep -c 'article-card' <新站>/index.html` ≥ `grep -c 'article-card' <参照站>/index.html`
- [ ] 教训来源: sub-travel首页10篇，同类型皆为12篇，整整少2篇

### C3.5 分类扩展后首页强制同步 (Category-Homepage Sync — 零容忍)
**新增分类页面≠用户可见。首页分类卡片必须同步更新。**

- [ ] **新增分类完成后必须更新首页Featured Categories** — category-*.html建了但首页不显示=用户永远找不到
- [ ] **验证命令（数字对比）**: 
  ```bash
  ls category-*.html | wc -l          # 实际分类页面数
  grep -c 'category-' index.html      # 首页分类卡片数（必须≥spec要求）
  ```
- [ ] **Spec必须明确首页展示几个分类卡片** — "Featured Categories: N张精选类别卡片"，不给模糊描述
- [ ] **View All链接必须指向分类总览页** — 如 `categories.html`，不是`#articles`锚点
- [ ] 教训来源: sub-beauty扩展12个新分类→72篇文章+12个category页面就位→Agent说done→首页仍只显示5个原始分类→新增内容对用户完全不可见

---

## 第四阶段: 验证审计 (Audit & Verification)

### A4.1 部署前审计 — 强制执行
- [ ] `python shared/pre_commit_audit.py` → **0 ERROR + 0 WARN** (1个ERROR或WARN即block)
- [ ] `python shared/check_portal_consistency.py` → **OK**
- [ ] `python shared/health_check_daily.py --quality` → **ALL OK**
- [ ] `python shared/refresh_sitemap.py <site_dir>` → 生成sitemap
- [ ] **WARN = 部署阻断** — 与ERROR同等对待，必须清零
- [ ] 绝不降低ERROR/WARN以求通过
- [ ] 教训来源: sub-career部署时30个标题过长WARN+36个semantic mismatch WARN未修即部署，违反"部署前多检查部署后少修改"原则

### A4.2 审计递归
- [ ] 审计必须扫描所有子目录HTML，不能只扫顶层文件
- [ ] `**/*.html` 递归，包含所有嵌套目录

### A4.3 审计脚本自检验证
- [ ] pre_commit_audit.py改检查逻辑后必须用已知正确/错误测试文件验证
- [ ] 防止自欺欺人式审计: ads.txt格式是 `pub-` 不是 `ca-pub-`

### A4.4 视觉抽检 (代码检测不出的问题)
- [ ] MD5不同但视觉重复 → 需人工/豆包视觉检查
- [ ] 图片与页面主题错配 → 代码审计查不出，必须视觉验证
- [ ] 分类索引页必须完整卡片网格 → 不能是3张Related Articles

### A4.5 链接审计
- [ ] 内部链接: 检查所有 `<a href>` 指向的文件是否存在
- [ ] Clean URL处理: 无 `.html` 后缀时 append `.html` 再检查
- [ ] **锚点链接验证**: `href="#xxx"` 必须对应目标页中存在的 `id="xxx"`，无匹配=死链
- [ ] **"View All"链接必须匹配当前版块**: Featured Categories的View All→分类列表页，Latest Articles的View All→文章列表页。禁止所有View All统一指向`#articles`锚点。教训: sub-beauty首页Featured Categories的"View All Guides"指向`#articles`→点完还在首页原地
- [ ] **链接逻辑合理性**: 不止检查"文件存在"，必须检查"链接有意义" — sitemap.html给搜索引擎不是给用户，"View All Articles"应链到articles.html而非sitemap
- [ ] **强制检查常见死链文件名**（2026-05-30新增）: `/privacy.html`→须为`/privacy-policy.html`，`/terms-of-service.html`→须为`/terms.html`，`/cookie.html`→须为`/cookie-policy.html`。误写文件名=全站死链。教训: demonslayer-site 30个角色页全部`/privacy.html`死链
- [ ] **Featured Categories卡片类型验证**: 分类区域只能包含分类卡片（`href="category-*.html"`），严禁混入文章卡片（`href="article-*.html"`含背景图/日期/阅读时间）。验证命令: `grep -c 'category-' index.html` = spec要求分类数，Featured Categories区域`grep -c 'article-[0-9]'` = 0
- [ ] 外部链接: 不强制验证但记录WARN
- [ ] OG/Canonical: 检查URL格式正确性
- [ ] Footer portal链接: 检查一致性
- [ ] 教训来源: sub-career 5个分类卡片链到不存在的#锚点，View All链到sitemap.html，文件存在审计通过但逻辑错误
- [ ] 教训来源: sub-beauty首页Featured Categories混入3篇article卡片+5个分类卡片混杂，文章卡片含background-image/日期/阅读时间但被放进分类网格

---

## 第五阶段: 部署 (Deployment)

### D5.0 部署前最后一道审核关口 (Pre-Deploy Final Gate) — 强制执行，不可跳过

**这是部署前的最后一道防线。违反此条=之前所有教训全部白费。**

执行时机: 所有代码/内容完成后，跑 `wrangler deploy` 之前。

#### D5.0.1 第一遍自检: Spec逐条对照
- [ ] 打开 `specs/<site-dir>.md`，从"页面结构"开始逐条读
- [ ] 每读一条，用 bash 命令验证数字: `ls | wc -l` / `grep -c` 而非肉眼
- [ ] 页面结构完整性: 所有HTML文件/图片/静态资源存在
- [ ] 分类设计: 每分类≥规定数量文章
- [ ] 质量与UX: 面包屑/ToC/FAQ/KeyTakeaways/进度条/返回顶部
- [ ] SEO: Schema/OG/Twitter/Canonical/Meta description
- [ ] 广告位: 数量/位置/纯自动广告
- [ ] 性能: preconnect/lazy loading/零JS
- [ ] 无障碍: skip-link/alt属性/语义化HTML
- [ ] 验收标准: 逐条跑spec底部的验收命令

#### D5.0.2 第二遍自检: MANDATORY_RULES逐条对照
- [ ] 打开 `specs/MANDATORY_RULES.md`，从P0到O7逐phase检查
- [ ] P0: rule_index匹配/Spec先行/先模版再批量
- [ ] T1: Footer/品牌/广告/图片遮罩/正则
- [ ] I2: 压缩/豆包验证/命名
- [ ] C3: HTML标签完整性/AI cliche/孤岛页面/事实准确性
- [ ] A4: pre_commit_audit 0 ERROR / portal_consistency / health_check
- [ ] 每项用 bash 命令输出数字，不凭感觉

#### D5.0.3 视觉验证 — 逐篇全量，不是抽查 (代码检测不出的问题)

**精雕=逐篇验证。抽样=不负责任。30篇文章=30次验证，不偷懒。**

- [ ] **逐篇打开每个HTML**，检查封面图是否加载（不是404/不是占位图）— 用 `curl -s -o /dev/null -w "%{http_code}"` 逐张验证每个img src
- [ ] **逐篇对比h1标题 vs 文章内容主题** — 标题必须准确反映内容，不能标题说A内容讲B
- [ ] **逐篇检查FAQ** — 必须针对文章具体主题，禁止泛化"Common questions about [category]"类FAQ
- [ ] **逐篇检查图片alt文本** — 必须描述图片内容，不是文件名
- [ ] **逐篇检查内部链接** — 锚文本必须与目标页面标题语义匹配，禁止"guide to X"链到讲Y的页面
- [ ] **所有banner/hero图片逐张豆包验证** — 检查面部裁切+内容匹配度，每张都过
- [ ] **所有封面图逐张豆包验证** — 30张封面逐张用doubao_vision.py验证图片内容与文章标题匹配
- [ ] 分类索引页逐页检查卡片完整性 — 全部条目卡片网格，不是3张Related Articles
- [ ] 图片MD5去重+视觉去重: 同一站内无视觉重复图片
- [ ] **验证脚本**: 用bash循环跑所有img URL的HTTP状态码，不凭肉眼"看起来没问题"
- [ ] 教训来源: sub-beauty站D5.0.3只抽查3篇→5张banner 404、11篇缺</body>、多个封面图与标题不匹配全部漏检。抽查=假过关。逐篇全量才能发现问题。

#### D5.0.4 两遍自查发现问题后的处理
- [ ] 发现问题→立即修复→回到D5.0.1重新开始(不是继续往下)
- [ ] 两遍全部通过+视觉验证通过 → 才能进入D5.1
- [ ] **严禁**: 发现WARN不修→"不影响部署"→跳过。WARN=ERROR=阻断部署，0 WARN才部署
- [ ] 教训来源: sub-career 30标题超标+36 semantic mismatch未修即部署，强哥当场指正

#### D5.0.5 多目标强制逐站验收 (禁止合并处理)
- [ ] **TodoWrite 必须拆成 N 个独立条目** — 用户指定N个目标时，每个目标独立一行。禁止写"修复3站footer"，必须拆成"修dailymedadvice footer"+"修rightsdaily footer"+"修main-site footer"
- [ ] **收尾前逐字回读用户原始消息** — 部署/汇报完成前，回读用户消息，逐目标验证。不是凭记忆，是逐字对
- [ ] **部署清单必须列出全部目标站名** — 少一个不部署
- [ ] **缺一个目标 = 不汇报完成** — 1站没部署不能说"3站部署完成"
- [ ] 教训来源: 2026-05-29 3站只部署2站，main-site被忘记。问题多的站吸走注意力，清单合并处理导致遗忘

#### D5.0.6 自查记录
- [ ] 每次部署前在对话中输出自查结果: 第一遍X项通过/X项修复, 第二遍X项通过/X项修复, 视觉验证X篇通过
- [ ] 记录到 `.claude/deploy_history.json` 的 `preflight_checks` 字段

---

### D5.1 部署前技术自检
- [ ] `python shared/preflight_check.py` → 4项全过 (CF Token/VPN/wrangler/磁盘)
- [ ] Flygo VPN检查: `tasklist /FI "IMAGENAME eq flygo.exe"` 先查进程，再curl验证
- [ ] CF Token已设置环境变量 `CLOUDFLARE_API_TOKEN`
- [ ] Windows下用 `npx.cmd` 不是 `npx`
- [ ] **Sitemap最终刷新**: `python shared/refresh_sitemap.py <site_dir>` → 确认URL数=HTML文件数。页面增删后sitemap不会自动更新，必须手动刷新。教训: sub-career新增articles.html+5个category页后未刷新sitemap，37→缺6页，GSC提交前才发现

### D5.2 CF Pages规则
- [ ] **CF Pages是Direct Upload模式** — Git push不触发部署
- [ ] 始终加 `--branch <production_branch>` — 错误分支→自定义域名不更新
- [ ] 部署前查production_branch: `curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" ...`
- [ ] 限流规则: 每批≤3并行，间隔5秒
- [ ] 项目名映射: `<site-dir>` → `<site-dir>` 去掉sub-前缀，加-jycsd后缀

### D5.3 部署回滚
- [ ] 部署前保存deployment ID到 `.claude/deploy_history.json`
- [ ] `python shared/rollback_deploy.py save <project> <deploy-id>`
- [ ] check_sync失败 → 自动回滚: `python shared/rollback_deploy.py rollback <project>`

### D5.4 单一部署源
- [ ] **本地是唯一部署源** — 只有本地wrangler CLI能部署到CF Pages
- [ ] 服务器禁止部署，不装wrangler，不配CF Token
- [ ] 服务器产出必须sync回本地后再部署

### D5.5 Git先于部署（零容忍 — 2026-05-30新增）
**部署前站点源代码必须全部在git tracking中。线上有代码但git无记录=灾难级风险。**

- [ ] 部署前验证: `git ls-files <site_dir>/ | wc -l` > 0
- [ ] 新站/新页面必须先 `git add <site_dir>/` + `git commit`，再 `wrangler deploy`
- [ ] 禁止从临时目录或未tracked目录直接部署
- [ ] 禁止部署未commit的改动
- [ ] 教训来源: demonslayer-site从临时目录部署上线，源文件丢失。41页全部从线上curl恢复，28张图逐个下载。坚决杜绝这种高风险行为

---

## 第六阶段: 部署后验证 (Post-Deploy)

### V6.1 check_sync强制闭环
- [ ] 部署 → `python shared/check_portal_consistency.py` → 有问题 → 修复 → 再部署 → 再check_sync
- [ ] 重复直到全绿，check_sync是最后一道防线

### V6.2 双URL验证
- [ ] Preview URL (`.pages.dev`) 验证内容
- [ ] 自定义域名验证内容
- [ ] **两者都正确才算部署成功**
- [ ] 用curl + grep验证关键元素: `grep -c 'article-card'`

### V6.3 ads.txt验证
- [ ] 逐站检查 `https://<domain>/ads.txt` 存在且含 `pub-` 开头的publisher ID
- [ ] 不是 `ca-pub-`，是 `pub-`

### V6.4 门户链接验证
- [ ] Footer 3个下拉select包含所有在线站点
- [ ] 每个选项指向正确的 `https://<domain>`
- [ ] 新站上线后，所有老站的footer也需更新(添加新站选项)

---

## 第七阶段: 运维监控 (Operations)

### O7.1 健康监控
- [ ] `python shared/health_check_daily.py` 定时运行 (cron: daily)
- [ ] 检查: 进程存活性 + 文章产出 + 僵尸进程 + 内容质量抽查
- [ ] 内容管道断1天 = 所有站停更

### O7.2 Sitemap自动刷新
- [ ] sitemap.xml基于文件系统扫描自动生成，禁止手动编辑
- [ ] 与 `refresh_sitemap.py` 联动
- [ ] 新文章发布后自动刷新

### O7.3 规则健康
- [ ] `python shared/rule_health_check.py` 定期运行
- [ ] 检测: 规则过期/矛盾对/孤立规则(不在MEMORY.md索引中)

### O7.4 跨站一致性
- [ ] site_config.json是唯一权威站点映射源
- [ ] 修改域名/站点 → 只改一处(site_config.json) → 所有脚本从这读
- [ ] 禁止多份映射散落

---

## 禁止事项总表 (Zero-Tolerance)

| # | 禁止事项 | 后果 |
|---|---------|------|
| 1 | 页面出现中国身份标识(江阴/车速递/China/JYCSD) | 海外用户信任崩塌，AdSense审核风险 |
| 2 | 手动广告位(`<ins class="adsbygoogle">`) | 广告不响应，用户体验差 |
| 3 | 图片阴影遮罩 | 图片失去光亮度，视觉效果差 |
| 4 | JS框架/构建工具 | 增加复杂度+体积，零收益 |
| 5 | 硬编码API Key/Token在代码 | 安全风险 |
| 6 | Footer用ul/li纯链接(非下拉菜单) | 跨站导航体验差 |
| 7 | 角色图片作Logo | 每页重复造成视觉疲劳 |
| 8 | 多行`<img>`标签 | 正则检测失效 |
| 9 | 编造数据/专家/研究引用 | 内容可信度归零 |
| 10 | emoji | 欧美受众觉得不专业 |
| 11 | 超过2行的注释 | 代码自解释 |
| 12 | 创建README/文档(除非明确要求) | 堆积无用文件 |
| 13 | 审计降级ERROR→WARN以求通过 | 自欺欺人，线上内容不达标 |
| 14 | 模板硬编码站点专属链接 | 全站死链 |
| 15 | `../images/`相对路径 | 子目录页面图片404 |
| 16 | 部署不查production_branch | 自定义域名永远不更新 |
| 17 | 修改其他子站文件(非批量工具) | 耦合混乱 |
| 18 | 未经验证说"done" | 90%实际未完成 |
| 19 | Agent prompt无备用方案 | Agent半途而废 |
| 20 | 全局替换后不grep验证零残留 | 漏改文件 |
| 21 | 模板未验证就批量生成内容 | 模板有遗漏=N篇文章全有同样遗漏=N轮修复 |
| 22 | 广告占位容器(ad-unit/虚线框/假Advertisement) | 纯Auto Ads一行脚本足矣，占位=画蛇添足+稀释内容密度 |
| 23 | Spec页面结构与老站不一致/缺页/写"无需单独HTML" | 全站死链，分类卡片/导航按钮全部失效 |
| 24 | D5.0.3视觉验证用抽查代替逐篇全量 | 5张banner 404+11篇缺标签全部漏检，抽查=假过关，精雕=逐篇过 |
| 25 | "View All"链接用`#articles`锚点指向首页 | 用户点"查看全部"→还在首页原地，必须指向实际列表页(/articles.html或分类索引页) |
| 26 | 多目标任务合并TodoWrite（写"修3站"而非3条独立条目）+ 收尾不回读原始消息 | 必漏目标。教训: 3站只部署2站，main-site被忘记。违者多目标任务直接阻断 |
| 27 | Featured Categories区域混入文章卡片（article-*.html含背景图/日期/阅读时间放进分类网格） | 用户看到分类区混杂文章，业务逻辑混乱。验证: `grep -c 'category-' index.html`=spec要求数, Featured区域`grep -c 'article-[0-9]'`=0 |
| 28 | 新增category-*.html页面后不同步更新首页分类卡片 | 分类页面存在但用户永远找不到=内容白做。验证: `ls category-*.html|wc -l` ≥ `grep -c 'category-' index.html` |
| 29 | 页面Schema/页脚出现zq30338@gmail.com或@qq.com邮箱 | 中国身份泄漏，T1.4违规。验证: `grep -rn 'zq30338\|@qq.com' *.html` = 0 |
| 30 | 首页Hero轮播大图与下方卡片网格使用同一批角色图片 | 用户看到同一角色出现两次=视觉重复=站点偷懒感。每个角色在首页最多出现一次。Hero和卡片区角色必须完全不同 |
| 31 | Anime/Game Hub引导页只有"Content being curated"占位文字 | Hub页是用户进入完整Wiki的第一入口，空空如也=用户立即跳出。每页必须至少有Top Characters卡片网格+Browse by Category分类链接+Visit Full Wiki按钮 |
| 32 | 负margin (`-mt-N`) 导致blockquote/文字被上方banner遮挡 | 负边距把文字拉入hero区域≈文字消失。必须用正margin隔开banner和后续内容 |
| 33 | 站点已部署上线但源代码未commit到git | 线上有代码但本地git无记录=灾难级风险。站点目录必须全部在git tracking中再部署。验证: `git ls-files <site_dir>/ | wc -l` > 0 |
| 34 | 分类目录页(index.html)缺失导致审计死链告警 | 每个 `/guides/<category>/` 目录必须有 `index.html`。缺了就是链接指向目录而非文件=死链 |
| 35 | HTML中使用 `&#9670;` / `◆` 等符号占位符代替真实内容 | 占位符=内容未完成。最终HTML中不得出现任何纯符号占位图/文本。用真实文字或图标替代 |
| 36 | OG标签/Schema/结构化数据缺失 | 每页必须有完整的OG(title/description/image/url/site_name/locale)+JSON-LD Schema。缺了SEO和社交分享失效 |

---

## 完成检查清单 (Implementation Checklist)

每个新站建设完毕后，逐项打勾:

### 模板层
- [ ] Footer 3个下拉select (Network/Content Sites/Game & Anime Wikis)
- [ ] 无硬编码分类链接
- [ ] 品牌: Myers Media, Jordan Myers, contact@jycsd.com
- [ ] 无中国身份标识
- [ ] 图片路径 `/images/` 绝对路径
- [ ] 图片无阴影遮罩
- [ ] Logo非角色图

### SEO/元数据
- [ ] title含主关键词，60-70字符
- [ ] meta description 150-160字符，每页唯一
- [ ] OG标签完整 (title/description/image/url/site_name/locale) — 六项缺一不可
- [ ] og:image 必须指向实际存在的图片（非default-og.jpg用于文章页）
- [ ] Twitter Card summary_large_image + twitter:image
- [ ] Canonical URL自引用
- [ ] Schema: Article + BreadcrumbList + Organization + WebSite + FAQ
- [ ] JSON-LD Schema必须合法JSON（非空非破损）
- [ ] 验证: `grep -c 'og:url' *.html` = 全站页面数, `grep -c 'application/ld+json' *.html` = 全站页面数

### 内容层
- [ ] 每篇文章 ≥1200字(内容站) / ≥500字(游戏动漫)
- [ ] 文章结构: ToC + Key Takeaways + 正文 + FAQ + 结论
- [ ] 阅读时间标注 + 最后更新日期
- [ ] 无AI cliché (7个黑名单)
- [ ] 无编造数据
- [ ] AI内容经HTML安全清洗
- [ ] 内部链接每篇≥2-3个

### 图片层
- [ ] 16:9横版 (1200x675)
- [ ] PIL压缩 (max_width=1200, quality=85)
- [ ] lazy loading (`loading="lazy"`)
- [ ] 描述性alt文本
- [ ] 无阴影遮罩

### 广告层
- [ ] 纯自动广告模式
- [ ] 首页3个广告位
- [ ] 文章页3个广告位
- [ ] 暗色底广告用浅色容器

### 审计层
- [ ] pre_commit_audit.py: 0 ERROR
- [ ] check_portal_consistency.py: OK
- [ ] health_check_daily.py --quality: ALL OK
- [ ] refresh_sitemap.py: 执行成功

### 部署层
- [ ] `git ls-files <site_dir>/ | wc -l` > 0 — 源代码已在git tracking中
- [ ] preflight_check.py: 4/4 PASS
- [ ] 保存deployment ID (回滚用)
- [ ] wrangler deploy --branch master
- [ ] 自定义域名验证通过
- [ ] ads.txt 存在且正确
- [ ] check_sync 闭环通过

---

**本规定如有新增或修改，立即更新，同步到所有spec文件。**
**本规定优先级高于任何单站spec，冲突时以本规定为准。**
