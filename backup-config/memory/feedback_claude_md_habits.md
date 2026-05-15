---
name: claude-md-habits
description: CLAUDE.md 上下文管理核心习惯——来自抖音博主布鲁斯一歇的Claude Code提效指南
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c818b428-f3ff-4ecf-88e6-780bb59129ff
---

# CLAUDE.md 使用习惯

## 核心原则
- CLAUDE.md 是项目的"长期记忆"，每次项目启动自动加载
- 控制在 200 行/800 字以内，写"禁止项"比写"推荐项"效果更好
- 多级层次：全局 `~/.claude/CLAUDE.md` → 项目 `./CLAUDE.md` → 本地 `./.claude.local.md`

## 关键习惯
- **每次 AI 犯错就更新 CLAUDE.md** — 把纠错变成永久规则
- **禁止项优先** — 明确列出"不要做什么"比"要做什么"更有效
- **技术规范写死** — 框架、库、部署方式一次性写清楚，避免每次对话重复交代
- **目录结构一目了然** — AI 能快速理解项目骨架

**Why:** 视频作者布鲁斯一歇的核心提效方法论——减少每次新对话的背景交代成本。

**How to apply:** 每个项目必须写 CLAUDE.md，包含项目概况、禁止项、技术规范、部署方式、可用技能。每次 AI 做错事就更新上去。
