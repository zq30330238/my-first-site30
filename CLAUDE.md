# CLAUDE.md — AdSense矩阵站点

## 项目概况
纯静态英文内容站矩阵，Tailwind CSS CDN + 零JS依赖，部署在 Cloudflare Pages。

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

## 技术规范
- Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- 字体：Roboto/Arial，正文≥16px，行间距1.5
- URL命名：`article/n-keywords-in-url` 格式
- 每篇文章1000-1500字，三段式：核心要点→细分讲解→场景应用
- 每页预留2-3个AdSense广告位
- 每子站独立robots.txt + sitemap.xml + ads.txt

## 部署
- 提交到git → `git push origin master` → Cloudflare Pages自动部署
- 每个子站绑定对应子域名到Cloudflare Pages项目

## 可用技能
- `/voice-chat` — 语音对话（listen.py按住左Ctrl说话，server.py桥接TTS播报）
- `douyin_parser.py` — 抖音视频解析+语音转文字（支持`--transcribe`）
- `vosk_server.py` — Vosk常驻转录服务（端口9877，避免每次加载模型）
- `ocr_screenshot.py` — 截图OCR识别
- `deploy.py` — 自动git提交推送

## 语音对话系统（重要）
- 桥接服务: `http://127.0.0.1:9876`（server.py 常驻运行）
- 转录服务: `http://127.0.0.1:9877/transcribe`（vosk_server.py 常驻，模型只加载一次）
- **每次回复后必须推送TTS**: `python -c "import urllib.request,json;urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:9876/response',data=json.dumps({'text':'<回复内容>'}).encode(),headers={'Content-Type':'application/json'}))"`
- 用户语音 → `/speech` → Claude处理 → 文字回复 → **必须POST到 `/response`** → 网页端Edge男声播报
- **禁止**只回复文字不推送语音，否则用户听不到Edge云飏男声
- 常驻服务保护：server.py和vosk_server.py崩溃后自动重启，listen.py发送前先检查端口
- **Hooks已配置** — SessionStart自动启服务，Stop自动推TTS，PreToolUse自动批准安全操作

## 多Agent编排规范（Ralph模式）
- **并行优先** — 独立子任务用Agent工具并行启动多个Agent，不串行排队
- **文件交接** — Agent间通过文件传递状态，不把所有上下文塞进主会话
- **循环迭代** — 大任务拆小步：计划→执行→验证→下一轮，每步结果写文件
- **失败恢复** — 关键状态持久化到文件，出错后从文件恢复，不从头开始
- **自我升级** — 定期检查已有工具是否有升级需求，主动搜索新技术资料优化自身
