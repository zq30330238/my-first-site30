# 服装站 SPEC（内部备忘录）

## 定位
- 品牌名：待定
- 域名：clothing.jycsd.com 或 fashion.jycsd.com
- 中式为主(70%) + 西式为辅(30%)
- 目标受众：海外对中国传统服饰好奇的用户 + 时尚爱好者

## 内容结构

### 中式服饰（主力）
```
chinese/
├── 56-ethnic-groups/        # 56民族服饰，每人一页
│   ├── han.html             # 汉族
│   ├── miao.html            # 苗族
│   ├── zhuang.html          # 壮族
│   ├── ... (按7大区组织)
│   └── index.html
├── dynasty-evolution/       # 朝代演变
│   ├── han-dynasty.html
│   ├── tang-dynasty.html
│   ├── song-dynasty.html
│   ├── ming-dynasty.html
│   ├── qing-dynasty.html
│   └── index.html
├── topics/                  # 专题
│   ├── qipao-history.html   # 旗袍简史
│   ├── dragon-phoenix.html  # 龙凤褂
│   ├── zhongshan-suit.html  # 中山装
│   └── tang-suit.html       # 唐装
└── index.html
```

### 西式服饰（辅料）
```
western/
├── fashion-week-trends/      # 时装周趋势分析（纯文字+CC0配图，不碰T台照）
│   ├── paris-ss2026.html
│   ├── milan-fw2026.html
│   └── index.html
├── classic-pieces/           # 经典单品史
│   ├── jeans.html
│   ├── little-black-dress.html
│   ├── white-shirt.html
│   └── trench-coat.html
└── index.html
```

### 对比板块
```
compare/
├── qipao-vs-evening-dress.html
├── eastern-western-wedding.html
└── index.html
```

### 通用页面
- index.html, about.html, contact.html, privacy-policy.html, cookie-policy.html, terms.html
- robots.txt, sitemap.xml, ads.txt

## 图片策略
- 来源：Unsplash / Pexels / Pixabay（全部CC0）
- 不需要rembg抠图，不需要豆包逐张验证
- 按文章主题搜索关键词下载高清JPG
- 每篇文章2-3张配图
- **图片必须有男有女** — 每民族男女服饰都要展示
- **优先全身照** — 完整展示服装轮廓和层次

## Pinterest引流策略（天然流量池）
- 全球最大图片社交平台，月活5亿+，核心用户=女性和生活方式爱好者，服装站目标受众高度重合
- 服饰图传播力远超建筑/科技类内容，56民族绚丽服饰天然适合Pinterest传播
- **落地项：**
  1. 每页额外生成2:3竖版封面（Pinterest标准比例），1000x1500
  2. 全站添加Rich Pins meta标签：`article:published_time`、`article:author`、`og:image:width`、`og:image:height`
  3. 每篇文章生成Pin描述模板，含热门关键词（Traditional Chinese Clothing、Ethnic Fashion、Hanfu Inspiration等）
  4. 创建分类Board：Ming Dynasty Hanfu、56 Ethnic Groups、East vs West Fashion、Classic Pieces History
  5. 申请Rich Pins认证，搜索结果带标题+作者，CTR更高

## 风格
- 明亮底，中国红accent (#c41e3a 或类似)
- 横向卡片布局，大图
- Tailwind CSS CDN

## 页面标准
- blockquote至少1个
- 完整meta+OG标签
- JSON-LD Schema
- AdSense广告位
- Footer下拉菜单

## 数据收集
- 56民族服饰资料：百度百科/维基百科英文版
- 朝代服饰：考古资料+博物馆公开信息
- 时装周趋势：Vogue Runway文字报道（只读文字，不盗图）
- 经典单品史：公开时尚史料

## 执行步骤
1. 建站骨架（index + 通用页面）
2. 收集56民族服饰资料 → character_data.json
3. 下载图片（Unsplash/Pexels CC0）
4. 渲染页面
5. 注册site_config.json + daily_articles.py
6. 审计 → 0 ERROR → 部署

## 页面预估
- 56民族: 57页(含index)
- 朝代: 6页(含index)
- 专题: 4页
- 西式趋势: ~8页
- 经典单品: 8页
- 对比: 3页
- 通用: 6页
- 首页: 1页
- **总计: ~93页**
