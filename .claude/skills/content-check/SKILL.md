---
name: content-check
description: 文章质量检查：字数、结构完整性、关键词密度、AdSense广告位
---

# 内容质量检查

检查文章是否符合站点标准。

## 检查项
- 字数：1000-1500字（HTML源码去标签后纯文本）
- 结构：含H2/H3标题至少3个
- 广告位：每页至少2个 AdSense 单元
- 面包屑导航和标签
- Schema JSON-LD 存在

## 执行
```bash
py shared/content_check.py <file>
```

## 标准
| 指标 | 标准 |
|------|------|
| 正文 | 1000-1500字 |
| H2 | 至少3个 |
| AdSense | 2-3个广告位 |
| Schema | NewsArticle JSON-LD |
