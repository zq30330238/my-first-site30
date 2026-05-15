---
name: workflow-habits
description: Claude Code 高效工作流习惯——上下文管理、Skills、Agents、Hooks
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c818b428-f3ff-4ecf-88e6-780bb59129ff
---

# Claude Code 高效工作流习惯

## 四件套工作流
1. **CLAUDE.md** — 长期记忆，项目规则写死
2. **Skills** — 专业技能库，重复任务封装为 `/command`
3. **Hooks** — 行为准则，自动拦截危险操作
4. **Agents** — 团队分工，并行任务用 Subagent 隔离上下文

## 上下文管理技巧
- `/compact` 在上下文变长时主动压缩，压缩比 99.9%
- Subagent 处理独立任务，避免主上下文污染
- Skills 三级渐进式加载：metadata → SKILL.md body → bundled resources
- Token 预算意识：200k 总预算，系统提示 2.5k，用户历史 12k，保留 4k

## 降本增效（用户强调）
- 后台任务不要反复检查进度，等通知即可
- 下载/安装等长时间操作，耐心等待不要轮询
- 上下文太长就 compact，别硬撑

**Why:** 抖音布鲁斯一歇的实战经验 + 用户多次强调"别浪费token"

**How to apply:** 每次对话开始时检查 CLAUDE.md，封装重复操作为 skill，独立任务用 Agent，上下文快满时主动 compact。
