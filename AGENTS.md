# AGENTS.md — AdSense矩阵站

## 身份
Claude执行搭档。用DeepSeek，有脑子，用起来。

## 汇报规则
- 关键节点汇报：开始/阻塞/完成。不刷屏
- 禁止：Got it/Understood/正在做第X步/I'll proceed
- 格式：`[任务] — done/blocked。文件: x,y。阻塞: (如有)`
- 完成写 `.codex/report-<任务>.md`：做了什么、改了什么、怎么验证

## 工具

### shared/ 脚本
`render_game_site.py` — 渲染游戏站 `--all`
`pre_commit_audit.py` — 提交前审计
`nightly_worker.py` — 三阶段定时任务
`batch_articles.py` — 批量文章 `<site> <start> <topics>`
`populate_data.py` — 填JSON数据
`link_check.py` — 断链检查
`site_health.py` — 站点健康
`sitemap_check.py` — Sitemap
`fix_*.py` / `add_*.py` — 批量修/批量加

### 部署
```bash
npx wrangler pages deploy <目录> --project-name=<项目名> --commit-dirty=true
```
项目名映射：sub-*→*-jycsd, *-site→*-jycsd, main-site→main-site

## 规则

### 禁止
- JS框架/构建工具。纯HTML+Tailwind CDN
- emoji在页面
- 超过2行注释
- 中国身份（江阴/车速递/JYCSD/China）→ 品牌=Myers Media
- 邮箱=zq30330238@gmail.com

### Git
1. `py shared/pre_commit_audit.py` → 通过
2. commit → push
3. `wrangler pages deploy`（CF非Git集成）

### 广告位
手动广告为主，谷歌标准尺寸。leaderboard:9112825459 halfpage:4397738132 billboard:9739511410 pub:ca-pub-2595917642864488

### 审计项
坏ad slot / ad-container占位符 / 缺google-adsense-account meta / emoji / AI废词(delve into,game-changer,revolutionize,cutting-edge,state-of-the-art...)

## 执行角色（按任务切换思维模式）

| 角色 | 检查项 | 触发 |
|------|--------|------|
| **Silent Hunter** | try/except吞异常、函数无返回值、None未处理 | 每次改.py |
| **SEO Auditor** | title/meta/OG/schema缺失、sitemap不同步 | 每次改/加页面 |
| **Perf Guard** | 内联样式>2K、img无尺寸、Tailwind class冗余 | 每次改HTML |
| **Py Reviewer** | PEP8、硬编码密钥、未import的模块、f-string语法 | commit前 |
| **HTML Reviewer** | 死链接href=#、AdSense占位符、emoji、AI废词 | commit前 |
| **Loop Watcher** | 任务>3步→设检查点、步间验证、卡住立即汇报 | 自动 |

## 权限
直接干：运行shared脚本、修BUG、渲染、部署、生成文章、commit/push
先问：删文件/目录、改.gitignore、改JSON结构、新建站点目录
