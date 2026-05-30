# sub-music — Music & Instruments (乐器/音乐制作)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sub-music/` |
| 域名 | music.jycsd.com |
| 站点名称 | Sonic Craft |
| 品牌色 | `#9333EA` (紫) + `#1E1B4B` (深紫底, 暗色变体) |
| 受众 | 15-40岁音乐爱好者 |
| 赛道CPC | $1-3 |
| 竞争度 | 低 |
| 模板类型 | content 标准模板 (暗色变体) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
sub-music/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   └── article-*.jpg (30张)
├── articles.html          # 全部文章列表页
├── category-guitar.html   # 分类1文章列表 (6篇)
├── category-piano.html    # 分类2文章列表 (6篇)
├── category-production.html # 分类3文章列表 (6篇)
├── category-theory.html   # 分类4文章列表 (6篇)
└── category-gear.html     # 分类5文章列表 (6篇)
```

参照站: sub-healthy (内容站模板)。页面结构必须与参照站一致。分类卡片链接到 category-*.html，View All 链接到 articles.html。

## 分类设计

### 1. Guitar Basics (吉他入门)
- **覆盖**: Chord diagrams, strumming patterns, fingerpicking, guitar types, tuning, beginner songs, barre chords

### 2. Piano for Beginners (钢琴入门)
- **覆盖**: Note reading, scales, chord progressions, hand independence, simple pieces, keyboard vs acoustic, pedal use

### 3. Music Production (音乐制作)
- **覆盖**: DAW comparison (Ableton/FL/Logic), MIDI basics, mixing fundamentals, mastering chain, sample selection, beat making

### 4. Music Theory (乐理)
- **覆盖**: Intervals, scales and modes, chord construction, circle of fifths, rhythm and meter, song structure analysis

### 5. Gear & Equipment (设备)
- **覆盖**: Audio interface guide, headphone recommendations, microphone types, studio monitor setup, budget home studio build

## 扩展类别（新增12个）

### 6. Drum & Percussion (鼓与打击乐)
- **标题**: Find Your Rhythm
- **覆盖**: Drum kit setup, stick technique, basic grooves, fills, electronic drums, percussion instruments, practice routines

### 7. Bass Guitar (贝斯)
- **标题**: Lay Down the Groove
- **覆盖**: Bass technique, slap bass, walking bass lines, gear guide, bass amp selection, playing with a drummer

### 8. Singing & Vocal Training (声乐)
- **标题**: Find Your Voice
- **覆盖**: Breathing technique, vocal warm-ups, pitch training, vibrato, belting vs head voice, microphone technique, vocal health

### 9. Electronic Music Production (电子音乐制作)
- **标题**: Build Beats from Scratch
- **覆盖**: DAW comparison (Ableton/FL Studio/Logic), synthesis basics, sampling, drum programming, arrangement, genre styles

### 10. DJ & Beatmatching (DJ与节拍匹配)
- **标题**: Move the Crowd
- **覆盖**: DJ controller guide, beatmatching by ear, phrase mixing, harmonic mixing, set building, rekordbox/Serato

### 11. Songwriting & Composition (词曲创作)
- **标题**: Write Songs That Connect
- **覆盖**: Song structure, chord progressions, melody writing, lyric techniques, co-writing, demo production, copyright basics

### 12. Home Studio Setup (家庭录音棚)
- **标题**: Record Like a Pro at Home
- **覆盖**: Audio interface selection, microphone guide, acoustic treatment, monitor speakers, recording workflow, budget setups

### 13. Mixing & Mastering (混音与母带)
- **标题**: Make Your Tracks Shine
- **覆盖**: EQ and compression, reverb and delay, stereo imaging, mix bus processing, mastering chain, LUFS and loudness standards

### 14. Music Marketing (音乐营销)
- **标题**: Get Your Music Heard
- **覆盖**: Spotify for Artists, playlist pitching, social media for musicians, email list building, PR basics, tour promotion

### 15. Live Performance (现场表演)
- **标题**: Own the Stage
- **覆盖**: Stage presence, monitor mixing, live sound basics, setlist design, gear reliability, performance anxiety management

### 16. Music History & Appreciation (音乐史与鉴赏)
- **标题**: Understand the Greats
- **覆盖**: Classical eras, jazz evolution, rock history, world music traditions, how to listen critically, influential albums

### 17. Band & Ensemble Playing (乐队与合奏)
- **标题**: Make Music Together
- **覆盖**: Finding bandmates, rehearsal efficiency, group dynamics, arrangement for bands, jam session etiquette, gig booking

## 特殊设计

- **暗色变体**: 整个站点使用深紫底(`#1E1B4B`)，文字白色，卡片用半透明深色背景
- 区别于其他内容站的亮色底，营造音乐工作室/暗房氛围

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 文章封面 | 30 | Unsplash (music/instruments/studio) |
| OG默认图 | 1 | 暗底+紫色logo |

**Unsplash搜索关键词**: guitar playing, piano keys, music studio production, musician performing, musical instruments, recording studio, audio equipment, DJ mixer, sheet music, concert stage

## 首页区块

1. **Hero**: 深紫底渐变 + "Discover Your Sound"
2. **Featured Categories**: 5分类卡片 (暗色卡片背景)
3. **Latest Articles**: 6篇
4. **Gear Picks**: 推荐设备
5. **AdSense**: 3个广告位

## 文章结构 (1000-1500字/篇)

三段式。乐器入门类含和弦图/指法描述。设备类含对比表。每分类6篇。

## CTR与流量增长策略

### 标题优化
- "Learn Guitar in 30 Days: A Complete Beginner's Roadmap"
- "7 Easy Songs to Learn on Piano (With Finger Positions)"
- 学习时间承诺+具体内容

### Meta Description
- 明确学习路径 + CTA
- 例: "Start playing guitar today with our 30-day beginner roadmap. Includes chord diagrams, strumming patterns, and 10 easy songs. No experience needed."

### Featured Snippet
- 和弦图(文字描述版)进paragraph snippet
- "How to tune a guitar?" → 步骤有序列表
- 设备对比进table snippet

### 内链策略
- 吉他↔钢琴↔乐理↔制作形成技能网络
- 乐器入门→乐理→设备推荐，学习路径链
- Related Articles + Read Next

### 内容新鲜度
- DAW/设备评测标注软件版本和评测日期
- 歌曲教程定期更新(流行新歌)
- 首页 "Trending Now in Music" 区块

### 回访机制
- 学习系列: "30-Day Guitar Challenge (Day 1-30)"
- 打印友好: 和弦图+指法表可打印

### 富文本摘要
- FAQ Schema
- HowTo Schema (演奏步骤)
- Review Schema (设备评测)
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 每篇文章 ≥1200字，乐器入门类含和弦图/指法描述/练习计划
- 文章结构: 导语钩子 → ToC → Key Takeaways → 正文3段 → 练习计划 → FAQ → 结论
- 阅读时间标注 + 最后更新日期
- 禁止AI cliché
- 和弦/音阶/指法数据需准确(可验证)

### 视觉质量 — 暗色变体特殊要求
- 封面图16:9，lazy loading，alt文本
- **暗色底对比度重点检查**:
  - 正文: `#E2E8F0`(浅灰) 在 `#1E1B4B`(深紫)上 → 对比度需≥4.5:1
  - 标题: `#C084FC`(亮紫) 在深底上 → 对比度需≥3:1(大文字)
  - 链接: `#A78BFA`(中紫) → hover时变亮至`#C4B5FD`
  - AdSense广告在暗色底上需有浅色卡片容器包裹
- 乐器图片: 背景干净，无杂乱
- 禁止图片阴影遮罩

### UX设计
- 面包屑 + 文章ToC(桌面sticky) + 相关文章(3篇) + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单，暗色主题
- **和弦图**: CSS绘制的弦线+品格网格(或用SVG inline)
- **练习计划**: 带checkbox的checklist(CSS模拟，打印友好)
- 音频术语: 信息框(Info Box)，浅紫边框

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + FAQ
- Meta/OG/Twitter/Canonical 完整
- 内部链接每篇2-3个

### 广告位
- 3个/篇，纯自动广告，禁止手动广告位
- **暗色底广告**: 用浅色卡片容器(`bg-gray-100 rounded`)包裹广告位，避免广告在暗色底上不可见

### 性能
- 预连接 + lazy loading + 零JS
- 暗色主题CSS变量在`:root`一次定义，全局复用

### 无障碍
- 语义化HTML + Skip to content + img有alt + 键盘可导航
- 暗色底上focus状态用亮色outline

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1-9步流程。CF项目名: music-jycsd。
**特别关注**: 暗色模板的WCAG AA对比度 + AdSense广告容器。

## 验收标准

```bash
ls sub-music/article-*.html | wc -l                      # >= 102
ls sub-music/category-*.html | wc -l                     # >= 17
grep -c 'article-card' sub-music/index.html              # >= 6
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
python shared/health_check_daily.py --quality
python shared/refresh_sitemap.py sub-music
```
