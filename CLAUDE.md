# CLAUDE.md — AdSense矩阵站点

## 项目概况
纯静态英文内容站矩阵，Tailwind CSS CDN + 零JS依赖，部署在 Cloudflare Pages。

## 三角架构：本地、远程服务器、CF Pages 关系

```
远程服务器 (206.119.168.150)          本地 Windows (d:\AI网站文件夹\)        Cloudflare Pages (CDN)
┌─────────────────────────┐         ┌──────────────────────────┐        ┌──────────────────────┐
│ 24/7 后台工人            │         │ 唯一代码源 + 唯一部署源    │        │ 生产环境              │
│                         │         │                          │        │                      │
│ collect_images_loop.py  │─sync ─▶│ 所有代码/渲染/审计        │─deploy▶│ ~20个独立项目         │
│ trend_scout.py          │         │ wrangler CLI 部署         │        │ Direct Upload 模式    │
│ ad_monitor.py           │         │ 自检清单强制执行          │        │ 自定义域名→master分支 │
│ /root/my-first-site30/  │         │                          │        │                      │
└─────────────────────────┘         └──────────┬───────────────┘        └──────────────────────┘
                                              │
                                              │ git push (仅备份)
                                              ▼
                                     ┌──────────────────┐
                                     │ GitHub            │
                                     │ 代码版本管理      │
                                     │ 不触发CF部署      │
                                     └──────────────────┘
```

**铁律：**
- **本地是唯一代码源** — 所有编辑/渲染/生成在本地完成
- **本地是唯一部署源** — 只有本地 wrangler CLI 能部署到 CF Pages
- **服务器只跑素材收集** — 图片下载、热点侦察、广告监控。不做文章生成/审计/部署。产出必须 sync 回本地
- **服务器禁止直接部署** — 服务器不装 wrangler，不配 CF Token
- **git push ≠ 上线** — Git 仅代码备份，CF Pages 是 Direct Upload 模式，无 Git 集成

## 新机器恢复
```bash
py recover.py
```
直接跑，报错缺什么就装什么。

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
- **禁止引入任何JS框架/构建工具** — 纯静态HTML + Tailwind CDN完全够用，引入框架只增加构建复杂度和体积，零收益
- **禁止修改其他子站文件** — 各子站独立目录、独立部署，改一个站点不该动其他站点。同时修改多个站用批量工具而非手动跨目录
- **禁止添加emoji到页面内容** — 目标受众欧美用户，emoji显得不专业。用文字表达而非图标
- **禁止写超过2行的注释** — 代码自解释
- **禁止创建README/文档** — 除非用户明确要求
- **禁止凭空编造内容/数据** — 所有事实性内容必须来自真实数据源。不得编造统计数据、研究引用、专家言论、用户评价、案例细节。AI 生成文章中的"studies show that..."、"according to research..."等内容必须有可验证的真实来源。不确定的信息标注为"general advice"而非"research proves"
- **绝对禁止在页面中出现任何中国身份标识** — 江阴/车速递/CheSuDi/Jiangyin/China/founded in China/JYCSD Network等不得出现。原因：海外用户对中国网站有信任偏见，AdSense审核对中文背景站更严格。对外品牌统一为 Myers Media，创始人 Jordan Myers。中文注册名仅限工商后台，永不对外

## 技术规范
- Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- 字体：Roboto/Arial，正文>=16px，行间距1.5
- 每篇文章1000-1500字，三段式：核心要点->细分讲解->场景应用
- 每页预留2-3个AdSense广告位
- 每子站独立robots.txt + sitemap.xml + ads.txt

## 部署前本地审计（强制）
- 每次 commit 前自动运行 `shared/pre_commit_audit.py`（.git/hooks/pre-commit）
- 审计不通过 -> commit 被拦截 -> 必须修复后重新提交

## 部署（重要：Direct Upload，非Git集成）
- CF Pages 是 Direct Upload 模式，git push 不会触发部署
- 流程：编辑 -> pre-commit 审计 -> commit -> push -> 自检清单 -> wrangler deploy -> 线上验证
- **部署前必须查 production_branch**：`curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/.../pages/projects/<project>" | python -c "import sys,json; print(json.load(sys.stdin)['result']['production_branch'])"`
- **始终加 `--branch <production_branch>`** — 错误的分支名会导致自定义域名不更新，preview URL 正确但线上永远是旧内容
- **部署前必须设置环境变量 `CLOUDFLARE_API_TOKEN`**（Token 值见 account memory）
- **限流规则** — 每批最多 3 个并行，间隔 5 秒
- 项目名映射：naruto-site->naruto-jycsd, onepiece-site->onepiece-jycsd, ...（完整列表见 三角架构文档）
- 部署后必须检查 footer 的 portal 链接、ads.txt 内容、图片是否正常
- **部署后用 Chrome DevTools 同时验证 preview URL 和自定义域名**，两者都正确才算部署成功
- git push 仅用于代码备份，不等于上线

## AI 角色调度
遇到任务 -> 查 `project_ai_team_panel.md` -> 按任务类型分派Agent。
核心原则：Flash默认执行，Pro仅对话+架构+验收，Python零LLM直跑。

## Agent 委派铁律（14条落地方案）

### 铁律1: 禁令代替指令
Agent prompt 用禁止句式而非指导句式。不说"为所有子站创建 articles.html"，说"必须处理以下6个目录，缺一不可：sub-healthy, sub-pets, sub-home, sub-finance, sub-tech, sub-travel。完成后逐个列出状态，未完成的报告原因。"

### 铁律2: 唱反调角色
Agent报告 done 后，我必须以否定前提验证：默认 agent 没完成 → 跑验证命令 → 看到数字才信。
"看起来没问题 ≠ 验证过"，"agent 说 done ≠ 实际完成"。

### 铁律3: 活可以分出去，思考不行
禁止外包理解。给 agent 的 prompt 必须是精确指令（具体文件路径、具体操作、具体验证命令），不允许"根据调查结果修复"这种模糊描述。我先消化信息、做出判断，再发指令。

### 铁律4: 验证数字内置
Agent prompt 末尾必须包含验证命令（bash 脚本），期望值写死在命令里。
agent 口头说"9篇文章"不可信，必须 `grep -c 'article-card' index.html` 输出 9 才算通过。

### 铁律5: 如实汇报
Agent 返回后，区分"已确认"和"agent 声称"。"agent 说修复了"≠ 修了，必须自己跑验证确认。

### 铁律6: 禁止"如果没有就跳过"
Agent prompt 每个"如果没有X"必须跟"就用Y替代"。不给 agent 留"跳过=完成任务"的选项。
错误: "如果没有图片就跳过" → 正确: "如果没有图片，用 https://images.unsplash.com/photo-XXX 作为默认图"

### 铁律7: 一次授权≠永久授权
部署/文件删除/push 等操作每次独立确认。不能因为之前批过就默认这次也可以。

## Pre-Task Interview Protocol
接受任何非平凡任务前：
1. 澄清范围 — 边界、涉及模块、不做什么
2. 识别风险 — 潜在陷阱和边缘情况
3. 定义成功标准 — 可验证的完成条件
4. 确认方案 — 用户点头再动手

## 核心工具链
- `shared/doubao_vision.py` — 豆包全模态（图/截图/视频），默认模型 `doubao-seed-2-0-lite-260428`
- `shared/douyin_parser.py` — 抖音短链->真实mp4->豆包解析
- `batch_generate_images.py` — Seedream 5.0 批量文章封面
- `shared/pre_commit_audit.py` — 部署前审计
- 语音系统: server.py(:9876 TTS桥接) + vosk_server.py(:9877 转录)，回复后必须POST TTS

## Karpathy 四原则 + gstack 角色分工
见全局 CLAUDE.md 和 `project_ai_team_panel.md`。

## Lessons Learned Log
格式：什么问题 -> 根因 -> 修复 -> 预防

### 2026-05-22
- [模型名记忆错误] 豆包模型名在代码/记忆/备忘录三处都不一致，反复Not Found。根因：记忆写入时未验证数据正确性。修复：从API `/v3/models` 拉取真实模型ID更新所有文件。预防：建记忆时必须验证数据源，代码优先于记忆。
- [部署分支—CRITICAL] 各项目的production_branch可能不同（naruto=main，其余=master），不能假设统一。部署前必须用API查每项目的production_branch。fix: naruto-jycsd从main改为master，15站全部统一。验证：自定义域名=production分支内容，不一致则域名永远不更新。
- [部署后必须验证自定义域名] preview URL正确≠自定义域名正确。CDN缓存+分支不匹配都可能导致自定义域名滞后。必须DevTools访问自定义域名确认内容，不能只看preview URL就收工。
- [CF Token限流] 7个站点并行部署触发CF rate limit(10429)→Authentication error(10000)→Invalid token(9109)。旧Token于2026-05-23失效，已切换至新Token（2031到期，见 account memory）。预防: 串行部署间隔5秒，单次不超过3个并行。
- [ads.txt全站检查] 22个动漫站缺ads.txt，10个游戏站假pub ID。预防: 部署前强制逐站检查ads.txt
- [审计脚本自欺欺人] ads.txt 检查用 `ca-pub-` 前缀查 ads.txt，但 ads.txt 标准格式是 `pub-`（不带 `ca-`），导致 14 站内容正确却误报 ERROR。根因：写审计规则时没对照 ads.txt 实际格式。预防：审计脚本必须加自检验证，用实际文件内容验证检查逻辑的正确性
- [蛇游戏] 蛇头追尾误判Game Over。fix: `s.cells.slice(0,-1)` 排除尾部
- [Memory游戏] 翻牌永不相配。fix: `fi/si`双变量替代复用`var f`
- [俄罗斯方块] 左右瞬移。fix: 顶层单次注册+80ms节流阀
- [审计降级=自欺欺人] 广告位不达标→降为warn→顺利过审部署→线上内容不达标。根因：用降级绕过标准而非做到位。修复：恢复error严格分级。预防：审计只设两档——error（block部署）和warn（不block但有记录），不以降低标准换取通过。
- [单一配置源] rightsdaily/dailymedadvice域名在check_sync.py写错→20站全错。根因：3个地方各自维护站点映射，人脑记不住。修复：建shared/site_config.json唯一权威源，check_sync.py和post-commit都从这读。预防：禁止多份映射散落，新增站点只改一处。
- [模板输出即合规] 465个页面缺blockquote→审计warn→逐一手动补。根因：模板没按标准输出。修复：改render_game_site.py两处模板，重渲所有游戏/动漫站。预防：模板必须在设计时就内嵌所有标准（blockquote+标题长度+广告位），输出天然合规，审计只是走过场。
- [部署后自检闭环] minecraft部署后footer selects不符。check_sync.py立即发现→再部署→再检→20/20一致。部署→check_sync→修复→再部署→再check_sync，闭环直到全绿。
