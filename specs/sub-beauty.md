# sub-beauty — Beauty & Skincare (护肤/美妆) — Glow Guide

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sub-beauty/` |
| 域名 | beauty.jycsd.com |
| 站点名称 | Glow Guide |
| 品牌色 | `#EC4899` (粉) + `#FDF2F8` (浅粉底) |
| 受众 | 18-45岁女性为主 + 男性护肤受众 |
| 赛道CPC | $3-5 |
| 竞争度 | 高 |
| 模板类型 | content 标准模板 |
| 品牌 | Myers Media / Jordan Myers |
| 总类别 | 17 |
| 总文章 | 102 (已有30 + 新增72) |

## 全部17个类别

### 已有类别 (5个 — 30篇)
1. **Skincare Basics** — 护肤基础
2. **Anti-Aging** — 抗老
3. **Acne Solutions** — 痘痘
4. **Makeup Tutorials** — 化妆教程
5. **Product Guides** — 产品导购

### 新增类别 (12个 — 每类6篇 = 72篇)

6. **Hair Care & Styling** — 护发/造型/头皮/发膜/洗发水选择/热工具防护
7. **K-Beauty & Trends** — 韩式护肤10步/玻璃肌/面膜/精华/气垫/蜗牛粘液
8. **Men's Grooming** — 男士护肤/剃须/胡须护理/男士香水/男士抗老
9. **Clean & Natural Beauty** — 纯净美妆/天然成分/DIY面膜/有机认证/可持续包装
10. **Body Care & Spa** — 身体乳/磨砂/干刷/自晒/身体痘/水疗
11. **Nail Art & Care** — 美甲/凝胶甲/甲健康/指甲艺术/甲油/修手
12. **Sun Protection** — SPF详解/矿物vs化学/补涂/UPF衣/晒后修复/晒黑安全
13. **Beauty Tools & Devices** — LED面罩/刮痧/滚轮/洁面仪/微电流/表皮剥脱
14. **Fragrance Guide** — 香水家族/选香/叠香/存储/小众vs商业/费洛蒙香
15. **Sensitive & Problem Skin** — 玫瑰痤疮/湿疹/无香料/低敏/屏障修复/斑贴测试
16. **Beauty on a Budget** — 药妆平替/低成本流程/DIY替代/促销时机/极简
17. **Bridal & Event Beauty** — 婚礼筹备/活动妆容/持久产品/上镜肌肤/应急修复

## 页面结构

```
sub-beauty/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── categories.html          # 全部17类别的列表页
├── articles.html            # 全部文章列表页
├── images/
│   ├── default-og.jpg / logo.svg / banner-*.jpg (6)
│   └── article-*.jpg (102张)
├── category-skincare.html (6篇) / category-antiaging.html (6篇)
├── category-acne.html (6篇) / category-makeup.html (6篇)
├── category-product-guides.html (6篇)
├── category-hair.html (6篇) / category-kbeauty.html (6篇)
├── category-mens.html (6篇) / category-clean-beauty.html (6篇)
├── category-body.html (6篇) / category-nail.html (6篇)
├── category-sun.html (6篇) / category-tools.html (6篇)
├── category-fragrance.html (6篇) / category-sensitive.html (6篇)
├── category-budget.html (6篇) / category-bridal.html (6篇)
└── article-1.html ~ article-102.html
```

## 首页区块

1. **Hero**: 品牌色渐变 + 6张banner轮播
2. **Featured Categories**: 6张精选类别卡片 + "View All →" → categories.html
3. **Latest Articles**: 6篇文章卡片 (3列网格) + "View All →" → articles.html
4. **AdSense**: hero下方 + 文章网格中 + footer上方

## 新增类别文章主题（每类6篇）

### 6. Hair Care & Styling
- Hair Type Guide: How to Identify Your Hair Type and Porosity
- Best Shampoos & Conditioners for Every Hair Type in 2026
- Heat Styling Without Damage: Temperature Settings and Heat Protectants
- Scalp Care 101: Why Scalp Health Determines Hair Growth
- Hair Masks and Deep Conditioning: DIY vs. Store-Bought
- How to Fix Common Hair Problems: Frizz, Breakage, and Split Ends

### 7. K-Beauty & Trends
- The 10-Step Korean Skincare Routine Explained for Beginners
- Glass Skin: What It Is and How to Achieve the Look
- Best Korean Sheet Masks for Every Skin Concern
- Essences, Ampoules, and Serums: Understanding Korean Layering
- Cushion Foundations: The K-Beauty Innovation Worth Trying
- Korean Beauty Trends Taking Over 2026: Slugging, Skin Flooding, and More

### 8. Men's Grooming
- Men's Skincare Basics: A Simple Routine Every Guy Should Follow
- Shaving Without Irritation: Razors, Creams, and Aftershave Guide
- Beard Care: Oils, Balms, and Grooming Tools for Every Beard Length
- Best Men's Fragrances for Every Occasion and Budget
- Anti-Aging for Men: What Works and What's Worth Skipping
- Men's Hair Care: Products and Styling for Every Hair Type

### 9. Clean & Natural Beauty
- What Clean Beauty Actually Means: Certifications and Ingredient Standards
- Natural Oils for Skincare: Which Ones Work and How to Use Them
- DIY Face Masks from Pantry Ingredients That Actually Work
- Organic vs. Natural vs. Clean: Understanding Beauty Labels
- Sustainable Beauty: Brands Reducing Packaging Waste in 2026
- Toxin-Free Beauty: Ingredients to Avoid and Safer Alternatives

### 10. Body Care & Spa
- The Complete Body Care Routine: Exfoliation, Moisture, and Protection
- Body Scrubs Compared: Sugar, Salt, Coffee, and Chemical Exfoliants
- Dry Brushing: Benefits, Technique, and Best Brushes to Use
- Self-Tanning Guide: Lotions, Mousses, and Application Tips
- Body Acne: Causes, Treatments, and Prevention Strategies
- At-Home Spa Day: Professional Treatments You Can Do Yourself

### 11. Nail Art & Care
- Nail Health Basics: Strengthening Weak and Brittle Nails
- Gel Nails at Home: Complete Kit Guide and Step-by-Step Tutorial
- Nail Art for Beginners: Tools, Techniques, and Easy Designs
- Dip Powder vs. Gel vs. Acrylic: Which System Is Right for You
- Cuticle Care and Hand Maintenance for Healthy Nails
- Nail Trends for 2026: Colors, Shapes, and Styles to Try

### 12. Sun Protection
- SPF Science: UVA, UVB, PA Ratings, and What They All Mean
- Mineral vs. Chemical Sunscreen: Which One Should You Choose
- How Much Sunscreen You Actually Need: Application and Reapplication Guide
- UPF Clothing and Accessories: Do They Really Work
- Sun Damage Repair: Can You Reverse Sunspots and Photoaging
- Sun Protection for Every Skin Tone: Debunking the Myth That Darker Skin Doesn't Need SPF

### 13. Beauty Tools & Devices
- LED Light Therapy Masks: Do At-Home Devices Actually Work
- Gua Sha and Jade Rolling: Ancient Techniques with Modern Benefits
- Sonic Cleansing Brushes vs. Hands: What Cleans Better
- Microcurrent Devices for Facial Toning: A Beginner's Guide
- Dermaplaning at Home: Tools, Technique, and Safety Tips
- The Rise of Beauty Tech: Smart Mirrors, Skin Scanners, and AI Analysis

### 14. Fragrance Guide
- Perfume Concentration Guide: EDP, EDT, EDC, and Parfum Differences
- Fragrance Families Explained: Floral, Oriental, Woody, and Fresh
- How to Choose a Signature Scent That Matches Your Personality
- Perfume Layering: How to Combine Scents Like a Pro
- How to Store Fragrances Properly to Make Them Last Longer
- Niche vs. Designer Fragrances: What Worth the Investment

### 15. Sensitive & Problem Skin
- Rosacea-Friendly Skincare: Triggers, Treatments, and Safe Products
- Eczema and Dry Skin: Barrier Repair Ingredients That Actually Work
- Fragrance-Free Beauty: Why It Matters and Best Products to Try
- Hypoallergenic Skincare: What the Label Really Means
- How to Do a Patch Test for New Skincare Products
- Building a Barrier-Repair Routine for Compromised Skin

### 16. Beauty on a Budget
- Best Drugstore Dupes for Luxury Skincare Products in 2026
- A Complete Skincare Routine Under $50: Products That Deliver
- DIY Beauty Alternatives: Kitchen Ingredients That Replace Expensive Products
- When to Splurge and When to Save: The Smart Beauty Budget Guide
- Multi-Use Beauty Products That Save Money and Space
- How to Time Your Beauty Purchases: Sales Cycles and Discount Strategies

### 17. Bridal & Event Beauty
- The Ultimate Bridal Skincare Timeline: 6 Months to Perfect Skin
- Wedding Day Makeup That Lasts: Long-Wear Products and Setting Techniques
- Pre-Event Skincare Prep: What to Do the Night Before and Morning Of
- Photo-Ready Makeup: How to Look Flawless in Every Lighting
- Emergency Beauty Fixes: Last-Minute Solutions for Pimples, Puffiness, and More
- Post-Event Skin Recovery: How to Reset After Heavy Makeup and Late Nights

## 文章结构 (1000-1500字/篇)

三段式: 核心要点 → 细分讲解 → 场景应用。文内含可操作步骤/产品成分说明。每类别6篇。

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 文章封面 | 102 | Unsplash + Pexels (按文章主题) |
| OG默认图 | 1 | 品牌色底+logo |
| Banner | 6 | 本地images/ |

## 验收标准

```bash
ls sub-beauty/article-*.html | wc -l                    # >= 102
ls sub-beauty/category-*.html | wc -l                   # >= 17
grep -c 'article-card' sub-beauty/index.html            # >= 6
python shared/pre_commit_audit.py                         # 0 ERROR
python shared/check_portal_consistency.py                 # OK
python shared/refresh_sitemap.py sub-beauty
curl -s https://beauty.jycsd.com/ | grep -c 'article-card'  # >= 6
curl -s https://beauty.jycsd.com/categories | grep -c 'category-'  # >= 17
```

## 实现步骤

1. 更新spec → 2. 生成1篇模板文章+P0.4验证 → 3. 批量生成72篇新文章+12类别页 → 4. 更新index/categories页 → 5. 下载+验证+压缩图片 → 6. 审计 → 7. 部署
