---
name: ralph-multi-agent-orchestration
description: Ralph多智能体编排——让AI长时间自主工作，从原理到实践
metadata: 
  node_type: memory
  type: reference
  originSessionId: c818b428-f3ff-4ecf-88e6-780bb59129ff
---

## Ralph多智能体编排

### 来源
- 抖音视频：老陈学徒说 — "Ralph+多智能体编排，让AI长时间工作 从原理到实践"
- 工具已安装：`@smplcty/ralph` (npm, v0.8.4)

### 核心概念

**Ralph Loop基础模式**：
```bash
while true; do
  claude --dangerously-skip-permissions -p "$(cat PROMPT.md)"
done
```
AI每轮看到相同的prompt但代码库已被上一轮改变，形成自我修正正反馈循环。

**多Agent分工**：
- 组织者(Orchestrator)：分配任务，收集结果
- 执行者(Worker)：并行处理具体任务
- 通过文件(HANDOFF.md/STATE.json)交接，不污染上下文

**关键原则**：
1. 计划→执行→验证→修正→再执行循环
2. 文件式状态传递（不在上下文中传全部信息）
3. 失败自动恢复（从历史记录继续）
4. 干净上下文每轮迭代
5. 并行化是效率关键

### 已应用到本项目的改造
- CLAUDE.md加入多Agent编排规范
- vosk_server.py常驻服务（模型只加载一次）
- douyin_parser.py流式处理（边下载边处理）
- 所有工具使用文件交接模式
