---
name: content-engine
description: Jycsd 矩阵站内容管线 — 新文章批量生成、审计、部署全流程自动化
origin: ECC (定制版)
---

# 内容引擎

为 6 个 AdSense 子站批量生成文章，全流程自动化。

## 管线流程
```
生成新文章 → pre-commit audit → git commit → git push → GitHub Actions 自动部署 CF Pages
```

## 生成新文章

当需要为一个或多个子站生成新文章时:

1. 确定目标子站和文章数量
2. 检查已有文章编号，确定下一个可用编号
3. 根据 `article-writing` skill 的模板生成 HTML
4. 确保每篇: 3 个 ad-unit + NewsArticle Schema + GA4 + 1000-1500字
5. 运行审计: `python d:/AI网站文件夹/shared/pre_commit_audit.py`

## 发布流程
1. 更新 index.html 侧边栏 Recent Posts (包含所有文章)
2. 更新 sitemap.xml (添加新文章 URL)
3. git add + commit + push
4. GitHub Actions 自动部署到 CF Pages
5. 验证线上: `curl -s https://<子域名>.jycsd.com/article-N.html`

## 恒创服务器 24h 管线
```
ssh root@206.119.168.150
cd /root/my-first-site30
python3 -u shared/expand_articles.py
```
服务器上 `expand_articles.py` 自动: 扩充短文章 → 审计 → commit → push

## 批量生成命令
为指定子站生成 N 篇新文章:
```
/claude "为 sub-healthy 生成 5 篇新文章，主题覆盖饮食计划、营养科学、健康食谱"
```

## 质量门禁
- pre_commit_audit 必须 0 error
- 每篇 1000-1500 词
- 3 个 ad unit + 全部 meta + Schema 完整
