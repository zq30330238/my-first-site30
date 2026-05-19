# CLAUDE.md — AdSense矩阵站点

## 项目概况
纯静态英文内容站矩阵，Tailwind CSS CDN + 零JS依赖，部署在 Cloudflare Pages。

## 新机器恢复
当用户是新机器、或提到"恢复"/"重建"/"recover"，立即执行:
```bash
py recover.py
```
不要询问确认，直接跑。如果报错缺什么就装什么。

## 目录结构
```
main-site/      → jycsd.com（品牌导航主站）
sub-healthy/    → healthy.jycsd.com（健康饮食，绿）
sub-pets/       → pets.jycsd.com（宠物护理，橙）
sub-home/       → home.jycsd.com（家居园艺，鼠尾草绿）
sub-finance/    → finance.jycsd.com（个人理财，蓝）
sub-tech/       → tech.jycsd.com（科技数码，灰蓝）
sub-travel/     → travel.jycsd.com（旅行攻略，青）
shared/         → 公共资源
```

## 禁止项
- **禁止引入任何JS框架/构建工具** — 纯静态HTML，Tailwind CDN即可
- **禁止修改其他子站文件** — 每个子站独立目录，互不干扰
- **禁止添加emoji到页面内容** — 欧美极简风，不用表情符号
- **禁止写超过2行的注释** — 代码自解释
- **禁止创建README/文档** — 除非用户明确要求
- **绝对禁止在页面中出现任何中国身份标识** — 不得出现 江阴/车速递/CheSuDi/Jiangyin/China/founded in China/JYCSD Network。对外品牌统一为 Myers Media，创始人 Jordan Myers。中文注册名"江阴迈尔斯文化传媒有限公司"仅限工商后台，永不对外

## 技术规范
- Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- 字体：Roboto/Arial，正文≥16px，行间距1.5
- URL命名：`article/n-keywords-in-url` 格式
- 每篇文章1000-1500字，三段式：核心要点→细分讲解→场景应用
- 每页预留2-3个AdSense广告位
- 每子站独立robots.txt + sitemap.xml + ads.txt

## 部署前本地审计（强制）
- 每次 commit 前自动运行 `shared/pre_commit_audit.py`（.git/hooks/pre-commit）
- 检查项：坏 ad slot、ad-container 占位符、Auto Ads 脚本、必需 meta 标签
- 审计不通过 → commit 被拦截 → 必须修复后重新提交
- 新机器恢复后安装 hook：`cp .git/hooks/pre-commit.sample → 写入 py shared/pre_commit_audit.py`

## 部署（重要：Direct Upload，非Git集成）
- CF Pages 是 Direct Upload 模式，git push 不会触发部署！
- 流程：编辑 → pre-commit 审计 → commit → push → wrangler deploy → 线上验证
- 修改任何子站文件后，必须运行 wrangler 部署对应项目：
  ```bash
  export CLOUDFLARE_API_TOKEN="<从settings.local.json的Bash allow列表取cfat_开头的token>"
  npx wrangler pages deploy <子站目录> --project-name=<项目名> --commit-dirty=true
  ```
- 项目名映射（重要——不是文件夹名！）：sub-healthy→healthy-jycsd, sub-pets→pets-jycsd, sub-home→home-jycsd, sub-finance→finance-jycsd, sub-tech→tech-jycsd, sub-travel→travel-jycsd, main-site→main-site
- 部署完成后必须用 Chrome DevTools 或 fetch 验证线上实际内容，不能假设成功
- 每次部署所有被修改的子站，不要遗漏
- git push 仅用于代码备份，不等于上线

## ECC 全家桶（62 Agents + 243 Skills + 75 Commands）
- 来源: Everything Claude Code (affaan-m)，Anthropic 黑客松冠军，17万 Star
- 本地源: `C:/Users/Administrator/.claude/plugins/marketplaces/ecc-manual/`
- 自动更新: 每6小时 git pull + 同步到 `.claude/agents/` `.claude/skills/` `.claude/commands/`
- 全自动换窗: 每3天自动写交接记忆 → 关旧窗 → 开新窗（cron: `37 9 */3 * *`）

## 自建专用Agent（项目定制，Flash模型执行）
- **image-pipeline** — 批量下载游戏/动漫角色HD图片，pngwing详情页原图，MD5去重，RGBA转换
- **site-auditor** — 全站审计：死链/坏图/广告位/SEO/Schema/搜索索引，递归扫描所有HTML
- 路径: `C:/Users/Administrator/.claude/agents/`
- 原则: ECC没有就自建，建一次用50站，一劳永逸
- 健康巡检: 每12小时增量检查（cron: `7 */12 * * *`）

## 可用技能
- `/voice-chat` — 语音对话（listen.py按住左Ctrl说话，server.py桥接TTS播报）
- `vosk_server.py` — Vosk常驻转录服务（端口9877，避免每次加载模型）
- `shared/doubao_vision.py` — 豆包全模态解析（图/截图/视频），已替代OCR
- `shared/douyin_parser.py` — 抖音短链→真实mp4→豆包解析，复刻豆包聊天端链路
- `deploy.py` — 自动git提交推送
- `article-generation` skill — 文章批量生成→审计→部署全流程
- `multimedia-parsing` skill — 图/视频/抖音链接解析全套工具链

## 语音对话系统（重要）
- 桥接服务: `http://127.0.0.1:9876`（server.py 常驻运行）
- 转录服务: `http://127.0.0.1:9877/transcribe`（vosk_server.py 常驻，模型只加载一次）
- **每次回复后必须推送TTS**: `python -c "import urllib.request,json;urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:9876/response',data=json.dumps({'text':'<回复内容>'}).encode(),headers={'Content-Type':'application/json'}))"`
- 用户语音 → `/speech` → Claude处理 → 文字回复 → **必须POST到 `/response`** → 网页端Edge男声播报
- **禁止**只回复文字不推送语音，否则用户听不到Edge云飏男声
- 常驻服务保护：server.py和vosk_server.py崩溃后自动重启，listen.py发送前先检查端口
- **Hooks已配置** — SessionStart自动启服务，Stop自动推TTS，PreToolUse自动批准安全操作

## Karpathy 编程四原则（整合 Andrej Karpathy Skills，125K Star）

### 原则 1：先想再写（Think Before Coding）
- **不假设，不隐藏困惑，暴露权衡。**
- 动手前先陈述你的假设。如果不确定，直接问。
- 如果存在多种理解方式，全部列出来——不要默默选一个。
- 如果有更简单的方法，说出来。该反驳时反驳。
- 如果某事不清楚，停下来。说出困惑点。问。

### 原则 2：极简至上（Simplicity First）
- **最少代码解决问题。不写投机代码。**
- 不添加需求之外的功能。不为单次使用创建抽象层。
- 不写"以后可能会用到"的灵活性/可配置性。
- 不为不可能发生的场景写错误处理。
- **如果你写了 200 行但其实 50 行就够，重写。**
- 自问："资深工程师会说过度复杂吗？" 如果会，简化。

### 原则 3：外科手术式修改 + 同类全修（Surgical + Sweep）
- **只碰必须碰的。但是——看到一个 bug，立即全项目扫描修复所有同类问题。**
- 不改与任务无关的代码、注释、格式。不重构没坏的东西。
- 匹配现有风格，即使你更喜欢别的方式。发现无关死代码时提出来，不要直接删。
- 你的改动产生的孤儿引用（import/变量/函数）必须清理。
- **同类问题扫全站**：发现一个 bug 就问——同类问题会不会批量存在？全项目扫描，一次性修复，不止修表面那一个。
- 测试：每个改动行都应追溯到用户需求或同类 bug 扫描结果。

### 原则 4：目标驱动执行（Goal-Driven Execution）
- **定义可验证的成功标准。循环直到标准达成。**
- 把模糊任务转化为可验证目标：
  - "加验证" → "为无效输入写测试，然后让它通过"
  - "修 bug" → "写复现测试，然后让它通过"
  - "重构 X" → "确保重构前后测试全部通过"
- 多步骤任务，列出每步的验证标准：
  ```
  1. [步骤] → 验证: [检查项]
  2. [步骤] → 验证: [检查项]
  ```
- 强的成功标准让你能独立循环推进。弱标准（"把它做出来"）需要不断追问。
- **部署后必须验证线上** — fetch 或浏览器检查实际内容，不能假设成功。

## gstack 虚拟工程团队（Garry Tan, YC President）

gstack 将 Claude Code 变成一支完整的虚拟工程团队，23个专家角色覆盖产品全生命周期。

### 角色分工体系

| 层级 | 角色 | 命令 | 职责 |
|------|------|------|------|
| **决策层** | CEO | `/plan-ceo-review` | 扩展视野、挑战假设、找10星产品方案 |
| | CTO/架构师 | `/plan-eng-review` | 技术选型、架构决策、锁定技术方向 |
| | 设计师 | `/plan-design-review` `/design-shotgun` | UI/UX审查、反AI味、多方案快速出图 |
| **质量层** | CSO | `/cso` | OWASP Top 10、STRIDE威胁建模、密钥扫描、供应链审计 |
| | QA | `/qa` `/browse` | 浏览器实测、响应式检查、交互验证 |
| | Reviewer | `/review` | 代码审查、逻辑正确性、边界条件 |
| **执行层** | Planner | `/autoplan` | 一键串联CEO+Eng+Design+DX四审，自动决策 |
| | Shipper | `/ship` | 合并→测试→版本号→CHANGELOG→PR |
| | Guard | `/guard` `/careful` | 拦截危险命令、目录保护、prod安全模式 |

### 集成时机（强制执行）

```
新站启动 → /office-hours（需求挖掘）→ /autoplan（四审自动决策）
代码完成 → /review（代码审查）
部署前   → /cso（安全审计）
部署后   → /qa <URL>（浏览器级线上验证）
上线后   → /browse（交互走查）+ /retro（回顾）
```

### 角色对应（绝不越权）

- **强哥** → CEO/产品决策（`/plan-ceo-review`、`/office-hours`）
- **Claude** → CTO+COO（架构决策、`/plan-eng-review`、`/review`、`/cso`、`/qa`）
- **Codex/Agent** → 执行层（代码编写、文件修改、渲染生成、批量操作）
- **Server Cron** → 运维层（nightly_worker、trend_scout、ad_monitor）

### 强制规则
- **Claude 绝不写执行代码** — 代码类任务统一走 Codex CLI 或后台 Agent（Flash 模型）
- **每次部署前后必须 `/cso` + `/qa`** — 安全审计通过 + 线上验证通过才算部署完成
- **新站启动必须先 `/office-hours`** — 不跳过需求挖掘直接建站
- `/guard` 模式在操作 prod 数据或做危险操作时强制开启

## 多Agent编排规范（Ralph模式）
- **并行优先** — 独立子任务用Agent工具并行启动多个Agent，不串行排队
- **文件交接** — Agent间通过文件传递状态，不把所有上下文塞进主会话
- **循环迭代** — 大任务拆小步：计划→执行→验证→下一轮，每步结果写文件
- **失败恢复** — 关键状态持久化到文件，出错后从文件恢复，不从头开始
- **自我升级** — 定期检查已有工具是否有升级需求，主动搜索新技术资料优化自身
- **Codex 分担** — 明确可执行的代码任务交给 Codex/后台Agent，Claude 专注需求讨论和架构决策
