---
name: seo-audit
description: 全站 SEO 审计：标题/描述长度、OG标签、canonical、Schema、死链检查
---

# SEO 审计技能

扫描全部7站79页面，检查SEO要素并生成报告。

## 触发条件
- 用户说"SEO审计"、"SEO检查"、"查SEO"
- 用户问"网站SEO怎么样"
- 修改页面后验证SEO完整性
- 定期巡检（服务器每天8:07自动执行）

## 执行
```bash
py shared/seo_audit.py
```

## 检查项
| 检查项 | 标准 |
|--------|------|
| Title长度 | 50-60字符 |
| Meta Description | 120-155字符 |
| OG标签 | og:title + og:description |
| Canonical | 必须有 |
| Schema JSON-LD | NewsArticle |
| Robots | index,follow |
| 重复检测 | 无重复title/desc |

## 输出
报告写入 `shared/seo-audit-report.md`，含每页详情和修复清单。
