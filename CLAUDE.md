# CLAUDE.md — AdSense矩阵站点

**每次新对话开始时，必须先读取交接文件：** `C:\Users\Administrator\.claude\projects\d--AI-----\memory\session_handover.md`

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
0. **强制规则匹配** — 先读 `C:\Users\Administrator\.claude\projects\d--AI-----\memory\rule_index.json`，按任务类型(new_site/deploy/fix_bug/generate_content/audit/batch_modify)找到对应规则列表，逐条Read确认约束。不确定类型则匹配所有。不查不动手。
   ```bash
   # 快速匹配: python -c "import json; d=json.load(open('C:/Users/Administrator/.claude/projects/d--AI-----/memory/rule_index.json')); [print(f'  {r}') for r in d.get('任务类型',{}).get('rules',[])]"
   ```
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

### 2026-05-30: demonslayer 27/28张角色图全是同一张家庭场景错图
- **问题**: 视觉审计发现demonslayer站28张图片中27张MD5完全一致（208KB），都是同一张"母亲与幼儿玩积木"家庭场景。文件名正确（tanjiro-kamado.png）但内容全错。rui.png是唯一不同的图片
- **根因**: 建站时图片生成/下载批量失败，所有文件被同一张错误图覆盖。文件名保留正确但内容全错——代码审计查不出（文件名对、文件存在、大小合理），必须视觉验证
- **修复**: Seedream 5.0重新生成27张角色图，PIL压缩至1200x675，豆包逐张验证。4张因Seedream性转偏见需二次生成（giyu/muzan/muichiro/obanai），加强提示词通过
- **预防**: (1) 新站建成后强制MD5去重检查，重复率>10%=异常 (2) 文件名正确≠内容正确，必须豆包验证 (3) 视觉审计层已写入MANDATORY_RULES.md

### 2026-05-30: Seedream 5.0 动漫男性角色性转偏见
- **问题**: Seedream 5.0即使提示词写"1boy, male, masculine"，仍有~14%概率生成女性版本。Giyu连续2次性转，Muzan/Muichiro各1次
- **根因**: Seedream对长发/精致/优雅男性角色有性别偏见，"1boy"不足以克服
- **修复**: 添加"masculine male physique, flat chest, adam's apple, broad shoulders, sharp jawline"等男性生理特征后通过
- **预防**: 动漫男性角色生成后必须豆包验证性别；高风险角色提示词强制加入男性生理特征

### 2026-05-30: SAO角色页hero图片完全缺失——第三次同类bug
- **问题**: agil/kikuoka/quinella三页hero区域只有空div，无img标签。页面第一个img来自Related Characters网格的其他角色图，导致视觉审计误判
- **根因**: 与之前valorant/fortnite hero缺失完全相同——页面模板未填充hero图。这是第三次出现
- **修复**: 三个HTML hero div内添加img标签+生成对应角色图
- **预防**: pre_commit_audit.py需增加空hero div检测。每次新站建设全量检查此模式

### 2026-05-30: CF API Token再次使用错误
- **问题**: 部署使用错误Token `cfut_GhVMSuf...`（已失效），三次部署静默失败
- **根因**: 未执行"CF API调用前必须读记忆文件"规则——对话上下文中Token是旧的
- **修复**: 从reference_all_accounts.md读取正确Token `cfut_OILkUKPY...` 重新部署
- **预防**: 每次部署前强制grep记忆文件确认Token，不信任对话上下文或会话摘要

### 2026-05-29: 每日管道产出假图+缺HTML标签 → 11内容站199文件全污染
- **问题**: beauty站102篇文章中72篇配图是AI编的假Unsplash URL(全部404)，11篇缺`</body>`标签。问题跨8站199文件：sub-beauty(91)/sub-career(91)/sub-healthy(3)/sub-pets(3)/sub-tech(3)/sub-travel(6)/sub-food(1)/sub-moto(1)。healthy站article-38/39共用假图default-og.jpg。5月28日的"修复"说解决了但实际未部署
- **根因**: (1) `batch_articles.py` prompt让AI"选一个Unsplash URL"→AI 100%编造假ID (2) AI生成HTML直接嵌入假URL，无下载验证步骤 (3) `collect_content_images.py` 后处理从未执行 (4) 生成的HTML缺`</body>`标签未被`quick_validate()`拦截 (5) `pre_commit_audit.py` 的假图检测只覆盖1-9位数字ID，漏了字母数字混合假ID (6) 5月28日修复后未部署，问题延续到29日
- **修复**: (1) `batch_articles.py`: 删除Unsplash URL要求，改用`/images/article-N.jpg`本地占位 (2) 199文件批处理：Unsplash URL→`/images/article-N.jpg` (3) 批量下载72张beauty图片(1200x675,PIL压缩) (4) 修11篇缺`</body>`标签 (5) `pre_commit_audit.py`: 新增`images.unsplash.com`到DEAD_IMAGE_DOMAINS (6) `MANDATORY_RULES.md`: 新增I2.5(禁止外部URL)+I2.6(图片必须实际存在)+I2.7(HTML结构完整性)+C3.2加强版(禁止AI编造URL)
- **预防**: (1) AI永远不能生成URL——所有资源引用必须基于实际文件系统状态 (2) 图片管道铁律: 下载→验证→压缩→入库→才能在HTML引用，不可跳过 (3) 部署前强制逐篇全量验证，不止抽查 (4) 修复后必须当日部署，不堆到"下次一起"。相关文件: shared/batch_articles.py, shared/pre_commit_audit.py, specs/MANDATORY_RULES.md
- **问题**: sub-beauty声称建完后，D5.0自检发现：5张banner 404（Unsplash ID全是编造的）、11篇文章缺`</body>`标签、4页面用错邮箱、全站`../images/`路径残留。这些问题在30篇文章中系统性存在，但我之前报告"站建完了"
- **根因**: (1) P0.4单篇验证走了形式——第1篇文章生成后没有逐条跑验证命令就批量了29篇，模板bug复制30次 (2) D5.0.3"抽查≥3篇"被当成上限——我只查了3篇，剩下27篇+6张banner没看 (3) Agent产出零验证——Agent说done我就信了，banner URL全是假的没人验证
- **修复**: (1) P0.4新增6条强制bash验证命令（HTML标签/图片路径/邮箱/AI cliche/封面图HTTP状态/审计），逐条跑不是凭感觉 (2) D5.0.3从"抽查≥3篇"升级为"逐篇全量验证"——30篇=30次，不偷懒 (3) 禁止事项总表新增第24条：抽查代替全量视觉验证 (4) 所有banner URL改为本地图片避免Unsplash假ID
- **预防**: (1) "精雕"=逐篇过，不是抽样 (2) 规则里的最低门槛（≥3）是下限不是目标——永远做全部不是做最少 (3) P0.4是最后一道批量前防线，这里走形式=后面全白费。相关文件: specs/MANDATORY_RULES.md P0.4 + D5.0.3

### 2026-05-30: 矛盾记忆毒化上下文 → demonslayer用错分支
- **问题**: demonslayer-site 用了 `--branch main` 部署。根因追溯到 `feedback_wrangler_deploy_branch.md` 记忆文件写着 "必须加 --branch main 参数"，这条错误记忆毒化了上次会话摘要，摘要写"demonslayer-jycsd uses production branch main"
- **根因**: (1) 记忆系统有两条矛盾记录——`project_cf_pages_branch_master.md`(正确:用master) vs `feedback_wrangler_deploy_branch.md`(错误:用main) (2) 上下文被错误记忆毒化后，我没有验证就直接信了 (3) 用户早就说过"全用master"，但没写成硬阻断规则
- **修复**: 删除 `feedback_wrangler_deploy_branch.md`；创建 `rule_cf_branch_master_only.md` 硬规则：全部用master、不查API、不验证、不信上下文。demonslayer重新用master部署
- **预防**: (1) 任何规则只允许一份记忆文件，发现矛盾立即删除错误版本 (2) 部署命令永远写死 `--branch master`，不准用变量/查API (3) 新人入职第一课：CF部署=master，没例外

### 2026-05-30: rotate_related.py硬编码onerror data URI → 658处假图跨6站
- **问题**: bleach/jjk/sao/tokyoghoul/onepiece/anime 6站84文件658处img标签含 `onerror="this.src='data:image/svg+xml,...'"` 占位符。JJK站100处fallback文字写着"Bleach"。pre_commit_audit未检测到(data URI在onerror属性而非src属性)
- **根因**: `shared/rotate_related.py:90` `build_grid_card()` 硬编码了onerror data URI fallback，文字写死"Bleach"+琥珀色。这模板被复制到所有动漫站。data URI在onerror而非src，审计脚本的正则没覆盖onerror属性
- **修复**: (1) rotate_related.py第90行删除onerror属性 (2) Agent清理84文件658处残留onerror (3) pre_commit_audit.py需新增onerror data URI检测规则
- **预防**: (1) 模板中绝不硬编码任何占位符(2) 审计正则搜索范围从`<img[^>]*src=`扩展到`<img[^>]*`全覆盖img标签所有属性 (3) 生成模板的占位文本必须参数化（站名/颜色），禁止写死
- **问题**: 用户多次指出 hero banner 太大（75vh），这次写 gothic-castle.html 模板又犯同样错误
- **根因**: 记忆系统是被动的——写了记忆但只在"事后记录"，不在"事前检查"。设计模板时跳过约束检查直接动手
- **修复**: Pre-Task Interview Protocol 新增第0步：设计类任务动手前强制 `grep` 记忆目录查相关约束，不查不动手
- **预防**: 任何创建/重写/设计任务，第一条动作不是写代码，是查记忆。相关文件: CLAUDE.md Pre-Task Interview Protocol

### 2026-05-27: 模板更新后本地HTML未重新生成 → 新旧两版并存
- **问题**: `site_templates.py` 的 footer 已升级为 3 下拉框，`daily_articles.py` 生成的新文章部署到线上是 3 下拉框。但本地旧 HTML 文件（如 rightsdaily/index.html）没被重新生成，仍是 1 下拉框。导致"本地是唯一代码源"被打破——查本地文件得出的结论和线上不一致
- **根因**: 模板引擎改了就改了，没有"模板改了→重渲染所有受影响页面"的流程
- **修复**: 暂无全局修复。当前手工确认了标准 footer 在 `site_templates.py` 第 545-605 行
- **预防**: (1) 查标准行为优先查 `shared/site_templates.py`，不以本地 HTML 为准 (2) 模板修改后必须重渲染全部受影响页面，不让新旧并存

### 2026-05-22
- [模型名记忆错误] 豆包模型名在代码/记忆/备忘录三处都不一致，反复Not Found。根因：记忆写入时未验证数据正确性。修复：从API `/v3/models` 拉取真实模型ID更新所有文件。预防：建记忆时必须验证数据源，代码优先于记忆。
- [部署分支—CRITICAL] 全部CF Pages项目统一用master，无例外。naruto-jycsd从main改为master后全站统一。禁止查API确认——不需要查，就是master。
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

### 2026-05-26: 后台进程残留导致新文章不断冒出来
- **问题**: daily_articles.py 用 Popen 在后台启动后进程未退出（PID 16336，13:12启动），持续生成新文章，修复速度赶不上新文章冒出的速度
- **根因**: subprocess.Popen 启动的子进程在主进程结束后未自动终止；没有进程监控机制
- **修复**: 手动 kill PID 16336
- **预防**: Popen 启动的长时间任务必须记录 PID 到文件；任务结束必须有明确的退出确认；跑 daily_articles.py 前先 `ps aux | grep daily_articles` 检查是否有残留进程

### 2026-05-26: TEMPLATE_SKELETON 硬编码 auto 分类链接导致全站死链
- **问题**: 13个内容站的文章导航栏全部出现 category-reviews/ev/buying/performance/chinese-brands 五个死链，142个文件受影响
- **根因**: `shared/site_templates.py` TEMPLATE_SKELETON（第505-509行）硬编码了 auto/moto 站专属的分类链接，所有内容站共用同一模板骨架，生成文章时不管站点类型全部注入这些链接
- **修复**: 删除5个硬编码分类链接，导航栏只保留 Home/About/Contact（每个站都有的通用页面）
- **预防**: 模板中绝不硬编码站点专属链接；所有导航项必须通过 SITE_CONFIG 按站配置，没有配置就不显示。相关文件: shared/site_templates.py

### 2026-05-26: SITE_CONFIG 硬编码 related_articles 导致 618 个 semantic mismatch 警告
- **问题**: 每个站配置了固定的3篇相关文章标题，但标题与实际文章 `<title>` 不匹配，产生618个语义不匹配警告
- **根因**: `render_article_html()` 直接从 `cfg["related_articles"]` 读取写死的标题，文章标题修改后未同步更新配置
- **修复**: 改为动态扫描站点目录下实际存在的 article-*.html 文件，读取真实 `<title>`，随机选取3篇
- **预防**: 所有"引用其他内容"的功能必须基于实际文件系统状态动态生成，不依赖手动维护的静态列表。相关文件: shared/site_templates.py

### 2026-05-26: blog-*.html 模板三连bug（../images路径 + 重复adsbygoogle + blog-0死链）
- **问题**: 生成的 blog-1.html / blog-2.html 文件存在三个系统性bug：图片用 `../images/` 相对路径、adsbygoogle.js 脚本重复两次、og:url/canonical 指向不存在的 blog-0.html
- **根因**: 游戏站博客模板未适配——图片路径应统一用 `/images/` 绝对路径；head 和 body 各注入了一次 adsbygoogle；blog-0.html 属于编造的占位URL
- **修复**: 9个 blog-*.html 文件的 `../images/` → `/images/`，删除重复的 adsbygoogle 脚本，blog-0.html → 对应 blog-N.html
- **预防**: 新建模板类型时必须跑完整审计后再批量生成；模板占位符必须用实际存在的URL，禁止编造占位链接。相关文件: site_templates.py 的游戏博客模板部分

### 2026-05-26: create_game_blog.py 模板修复遗漏（同类bug跨文件未排查）
- **问题**: 上次修复了 site_templates.py 的博客模板三连bug，但 daily_articles.py 今天生成的10个新blog文件仍有同样的 `../images/` + 双adsbygoogle 问题
- **根因**: create_game_blog.py 是 daily_articles.py 实际调用的blog生成脚本，有自己的HTML模板（`generate_blog_html()`），上次修复时只改了 site_templates.py 没改这个文件。"同类问题立即排查"原则执行不到位——改了site_templates.py却没grep全项目找其他用了 `../images/` 的文件
- **修复**: 修复 create_game_blog.py 三处：① extract_from_index 中 strip adsbygoogle ② 删除 else 分支重复 adsbygoogle ③ `../images/` → `/images/`；同时修复10个新生成的blog文件
- **预防**: 修模板bug时强制执行 `grep -r "同样的错误模式" --include="*.py" shared/` 全项目扫描，修一处查全部。相关文件: shared/create_game_blog.py

### 2026-05-27: Agent prompt 过大导致静默失败（0输出0文件）
- **问题**: 一个 Agent 构建欧美建筑站61页全部内容，prompt 包含完整 HTML 模板+Footer+61页详细规格+验证命令，Agent 静默失败：output 文件 0 字节，0 个 HTML 文件生成
- **根因**: prompt 过大超出 haiku 模型处理能力；61页规格+完整HTML模板塞进一个 prompt = token 爆炸
- **修复**: 拆成单页 Agent（gothic-castle.html 模板页），prompt 只含一页规格，Agent 成功完成
- **预防**: Agent 内容生成类任务单次不超过 5 页；大型站点分 section 并行启动多个 Agent（castles/residential/styles/interiors/landmarks/compare 各一个），每个 Agent prompt 只含该 section 的页面规格+通用模板引用。相关文件: 无

### 2026-05-27: 首页卡片图文错配系统性Bug — 14处卡片标题/链接/背景图互不匹配
- **问题**: Food站首页8个卡片（Featured Carousel 2 + Latest Recipes 6）、Entertainment站5个、sub-healthy 1个，共计14处卡片标题、href链接、背景图URL三者互相不匹配。如"Jianbing"卡片链到article-46(Roujiamo)、背景图也是肉夹馍。此问题跨3站同时存在。
- **根因**: 5个脚本Bug：(1) `insert_index_card()` 用 `grid md:grid-cols-2 lg:grid-cols-3 gap-8` 精确匹配class，Food站的 `grid-cols-1 md:grid-cols-2` 变体匹配失败，卡片从未被动态插入，全是写死的旧链接 (2) `collect_content_images.py` 的 `update_article_html()` 只在body前2000字符搜索已有img，FOOD模板封面图远超此窗口→找不到则插入第二个img→同一图片出现两次 (3) `render_article_html()` 朴素str.replace()不做HTML转义，AI内容含 `</head>`/`<body` 字符串直接破坏HTML结构 (4) `quick_validate()` 只检查DOGTYPE/GA4/AdSense，从不检查 `</head>`/`<body>` 标签完整性 (5) 缺少AI输出安全清洗步骤
- **修复**: 修复5个脚本Bug + 修复14处卡片错配 + 5篇损坏文章 + 7篇无图片 + 7篇重复图片 + 48处图片阴影遮罩（food/auto/moto）
- **预防**: (1) 网格匹配用 `grid-cols-2 lg:grid-cols-3` 子串而非精确class (2) 图片搜索扩展到整个body (3) AI内容替换前强制清洗HTML危险字符 (4) quick_validate()强制检查 `</head>`/`<body>`/`</body>`/`</html>` 四个标签 (5) 每次生成新文章后自动对比卡片标题、链接href、背景图编号三者一致性。相关文件: shared/site_templates.py, shared/create_articles.py, shared/collect_content_images.py, shared/daily_articles.py

### 2026-05-27: 图片阴影遮罩全局禁止
- **问题**: Food站Featured Carousel有 `bg-black/40` 半透明遮罩+菜谱卡片 `bg-gradient-to-t from-black/70` 渐变遮罩，auto/moto站有 `linear-gradient(rgba(0,0,0,.85)...)` + `bg-black/50` 遮罩。图片表面像盖了一层颜色，严重影响视觉效果
- **根因**: 模板设计时为了白色文字可读性加了遮罩层，但牺牲了图片原有的光亮度
- **修复**: 删除全部48处遮罩div，改用 `text-shadow: 0 2px 8px rgba(0,0,0,0.8)` 保证文字可读性
- **预防**: 全局禁止在图片上使用任何bg-black/、bg-gradient-to-t、linear-gradient(rgba())等覆盖层。卡片级box-shadow悬浮效果不受限制。规则已存入memory/feedback_no_image_overlay.md

### 2026-05-29: 多目标任务漏掉一个 — 3站只部署了2站
- **问题**: 用户明确指定 jycsd.com/dailymedadvice.com/rightsdaily.com 三个站。修bug时 dailymedadvice+rightsdaily 问题多(3-4个)，main-site 仅1个问题。注意力被问题多的站吸走，部署时忘了 main-site，用户质问才发现
- **根因**: (1) TodoWrite 条目写"3站"合并处理，不是每个站独立一行 (2) 收尾时没回读用户原始消息逐条对 (3) 凭脑子记清单=天然会漏
- **修复**: 补充修复 main-site 33个文件(加 Jordan Myers)，部署验证上线
- **预防**: 违者下次同类任务直接阻断。多目标任务强制执行三条: (1) TodoWrite 拆成 N 个独立条目，每个目标一行，不写"合并处理3站" (2) 部署/汇报前回读用户原始消息逐字核对 (3) 缺一个目标不汇报完成

### 2026-05-27: 域名替换后未全量验证 → sitemap.xml/robots.txt 漏改
- **问题**: 域名从 global-architecture 改为 western-architecture，批量替换了 60 个 HTML 文件，但漏了 sitemap.xml（60个旧URL）和 robots.txt（1个旧URL）。GSC 提交 sitemap 时报"无法抓取"
- **根因**: 批量替换后只确认了 HTML 文件，没跑 `grep -r "old-domain" --include="*.xml" --include="*.txt"` 全量验证。替换范围假设只有 .html，实际 xml/txt 也有旧域名
- **修复**: 修复 sitemap.xml (60处) + robots.txt (1处)，重新部署
- **预防**: 域名替换/全局搜索替换后强制执行 `grep -rl "旧字符串" 目录/` 确认零残留，不限文件类型

### 2026-05-29: 首页Featured Categories混入文章卡片 — 业务逻辑污染
- **问题**: beauty首页"Featured Categories"区域6张卡片中3张是文章卡片（article-31/32/33，含background-image/日期/阅读时间），只有3张是真正的分类卡片。首页分类区域变成了文章+分类混杂
- **根因**: 内容更新脚本把文章卡片插入到了分类网格，没有区分两种卡片类型（分类卡片=图标+描述+href→category-*.html，文章卡片=背景图+日期+阅读时间+href→article-*.html）
- **修复**: 删除3篇混入文章，补第6个分类(Hair Care & Styling)，View All从`#articles`改为`categories.html`
- **预防**: (1) 修改首页卡片后强制验证: `grep -c 'category-' index.html` 检查分类卡片数=spec要求数 (2) `grep 'article-card.*article-[0-9]' index.html` 检查Featured Categories区域不包含文章卡片 (3) 每个分类卡片href必须指向category-*.html

### 2026-05-29: 新增12个分类后首页未同步 — 后端有了前端没有
- **问题**: beauty站按spec新增12个分类（hair/kbeauty/mens/clean-beauty/body/nail/sun/tools/fragrance/sensitive/budget/bridal），72篇文章+12个category-*.html全部就位。但首页Featured Categories仍只显示5个原始分类，新增分类对用户完全不可见
- **根因**: 分类扩展=两步操作（建category页面+写文章）+ 一步遗漏（更新首页分类卡片）。Agent做完前两步就报告"done"，第三步没人触发
- **修复**: 首页新增第6个分类卡片(Hair Care & Styling)，View All指向categories.html列出全部17分类
- **预防**: (1) 扩展分类的spec必须写清楚"更新首页Featured Categories卡片到N个" (2) 所有分类页面创建完毕后强制执行: `ls category-*.html | wc -l` vs `grep -c 'category-' index.html` 对比数字

### 2026-05-29: 个人邮箱zq30338@gmail.com泄漏到4个页面Schema
- **问题**: contact/cookie-policy/privacy-policy/terms 四个页面的Organization Schema中contactPoint email为zq30338@gmail.com，违反T1.4品牌规范
- **根因**: 模板中Schema的email字段未被替换为contact@jycsd.com，Agent生成时直接从模板复制未检查
- **修复**: 4个文件全部替换为contact@jycsd.com
- **预防**: pre_commit_audit.py已有zq30338检查但此前WARN被忽略。严格执行A4.1: WARN=ERROR=阻断部署，0 WARN才部署。相关文件: sub-beauty/contact.html, cookie-policy.html, privacy-policy.html, terms.html

### 2026-05-29: 目录名泄漏到OG图片URL — sub-beauty.jycsd.com
- **问题**: beauty站30篇文章的og:image全部使用 `https://sub-beauty.jycsd.com/images/article-N.jpg`，`sub-beauty` 是本地目录名不是真实域名。真实域名是 `beauty.jycsd.com`
- **根因**: 文章生成脚本在构建OG图片URL时使用了目录名（`sub-beauty`）而非站点配置中的真实域名（`beauty.jycsd.com`）。DOMAIN变量映射错误
- **修复**: 30个文件 `sub-beauty.jycsd.com` → `beauty.jycsd.com` 批量替换
- **预防**: (1) pre_commit_audit.py新增检查: `grep -r "sub-[a-z-]*\.jycsd\.com" --include="*.html"` 检测目录名泄漏到URL (2) 文章生成时必须从site_config.json读domain字段构建URL，禁止用目录名拼接域名

### 2026-05-29: DDGS图片搜索返回中国政治徽章 → 内容错配到英文站
- **问题**: career站 article-71 (Growth Hacking) 配图是中国共青团徽章。article-54/87/99 三张竖版图比例错。5个分类页 hex 颜色代码(#7c3aed等)被Agent当成标题文字写进 h3 和 img alt。
- **根因**: (1) DDGS图片搜索不审查内容来源 → 搜索词含中文关键词时返回中国政治图片 (2) 图片下载后无视觉验证步骤 (3) Agent生成分类页时把品牌色hex当占位文本，未替换成真实标题 (4) 无图片比例自动检查
- **修复**: 替换4张问题图(71/54/87/99) + 5分类页30处hex→真实标题 + pre_commit_audit.py新增 check_image_dimensions() 自动拦截竖版/小图
- **预防**: (1) 所有图片下载必须跑豆包视觉验证后才入库，DDGS结果不可信 (2) 图片比例<1.0(竖版)或宽度<800px自动拦截为ERROR (3) Agent生成HTML后必须正则检查 `#[0-9a-fA-F]{6}` 不在可见文本中 (4) 豆包API不可用时禁止跳过视觉验证，用Unsplash替代DDGS。相关文件: shared/pre_commit_audit.py check_image_dimensions()
