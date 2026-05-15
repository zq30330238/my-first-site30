---
name: sitemap-check
description: 验证 sitemap.xml 完整性，确保所有页面被收录
---

# Sitemap 检查

验证每个子站的 sitemap.xml 是否包含所有 HTML 页面。

## 执行
```bash
py shared/sitemap_check.py
```

## 检查项
- sitemap.xml 文件存在
- 所有 .html 页面都在 sitemap 中列出
- URL 数量与页面数量匹配
