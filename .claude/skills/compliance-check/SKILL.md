---
name: compliance-check
description: 检查 robots.txt 和 ads.txt 合规性，确保 AdSense 收录要求满足
---

# 合规检查

验证所有站点的 robots.txt 和 ads.txt 是否符合 Google AdSense 要求。

## 检查项
- robots.txt: User-agent, Allow, Sitemap 声明
- ads.txt: google.com, pub- 发布商ID

## 执行
```bash
py shared/compliance_check.py
```
