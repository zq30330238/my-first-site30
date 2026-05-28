# 中式建筑站 SPEC（内部备忘录）

## 定位
- 品牌名：待定
- 域名：chinese-architecture.jycsd.com 或 architecture.jycsd.com
- 中华建筑+中式室内装修
- 受众：海外对中国建筑/中式美学好奇的用户 + 建筑师/室内设计师

## 内容结构

### 住宅类型
```
residential/
├── single-family-villa.html    # 独栋别墅
├── townhouse.html              # 联排别墅
├── duplex.html                 # 双拼别墅
├── stacked-villa.html          # 叠墅
├── courtyard-estate.html       # 中式别院
├── high-rise.html              # 高层住宅
├── mid-rise.html               # 多层住宅
└── index.html
```

### 中式风格流派
```
regional-styles/
├── hui-style.html              # 徽派建筑（白墙黛瓦马头墙）
├── su-style.html               # 苏式园林（苏州园林）
├── beijing-courtyard.html      # 京派四合院
├── lingnan-style.html          # 岭南建筑（镬耳屋）
├── chuanxi-style.html          # 川西民居
├── minnan-style.html           # 闽南建筑（土楼/红砖厝）
├── tibetan-style.html          # 藏式建筑
├── mongolian-yurt.html         # 蒙古包
└── index.html
```

### 建筑元素专题
```
elements/
├── dougong.html                # 斗拱
├── roof-types.html             # 屋顶形制（庑殿/歇山/悬山/硬山/攒尖）
├── courtyard-garden.html       # 中式庭院/园林
├── screen-wall.html            # 照壁/影壁
├── window-lattice.html         # 花窗/漏窗
├── wood-carving.html           # 木雕/砖雕/石雕
├── fengshui-basics.html        # 风水基础
└── index.html
```

### 中式室内装修
```
interior/
├── new-chinese-style.html      # 新中式
├── classical-chinese.html      # 古典中式（红木/屏风/博古架）
├── ming-qing-furniture.html    # 明清家具
├── tea-room-design.html        # 茶室设计
├── chinese-color-palette.html  # 中式配色（中国红/帝王黄/青花蓝）
├── silk-brocade-decor.html     # 丝绸/织锦软装
└── index.html
```

### 知名建筑巡礼
```
landmarks/
├── forbidden-city.html         # 故宫
├── summer-palace.html          # 颐和园
├── temple-of-heaven.html       # 天坛
├── humble-administrator.html   # 拙政园
├── fujian-tulou.html           # 福建土楼
├── potala-palace.html          # 布达拉宫
└── index.html
```

### 通用页面
- index.html, about.html, contact.html, privacy-policy.html, cookie-policy.html, terms.html
- robots.txt, sitemap.xml, ads.txt

## 图片策略
- 来源：Unsplash / Pexels / Pixabay（CC0）
- 不需要rembg，不需要豆包验证
- 每篇文章2-3张建筑实景摄影
- 特殊需求：中国传统建筑细节图（斗拱/屋顶/花窗），如果CC0图库不够，可用Wikipedia Commons

## 风格
- 明亮底
- accent色：中国红 #c41e3a 或 朱砂红 #e74c3c
- 横向卡片大图布局

## 页面标准
- blockquote至少1个
- 完整meta+OG标签
- JSON-LD Schema (Article 或 WebPage)
- AdSense广告位
- Footer下拉菜单

## 页面预估
- 住宅类型: 8页(含index)
- 风格流派: 10页
- 建筑元素: 8页
- 室内装修: 7页
- 知名建筑: 7页
- 通用: 6页
- 首页: 1页
- **总计: ~47页**
