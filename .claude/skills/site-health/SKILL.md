---
name: site-health
description: 统一站点健康检查：SEO + 死链 + 内容质量 + Sitemap 一次性全检
---

# 站点健康检查

运行全部检查项并生成统一报告。

## 检查项
- SEO：Title/Meta长度、OG标签、Canonical、Schema
- 链接：死链检测 + 孤岛页面识别
- 内容：字数、H2结构、AdSense广告位
- Sitemap：完整性验证

## 执行
```bash
py shared/site_health.py
```

## 输出
统一报告写入 `shared/site-health-report.md`，含汇总表和逐页问题清单。
