# 新机器恢复指南

## 你需要手动做的

### 1. 装 Claude Code + CC-Switch
```
Claude Code    按官方文档安装
CC-Switch      https://github.com/farion1231/cc-switch/releases（下载 .msi 安装）
```

### 2. 配置 CC-Switch 接入 DeepSeek
```
打开 CC-Switch → 点 + → DeepSeek 预设
  Base URL:   https://api.deepseek.com/anthropic
  Auth类型:   ANTHROPIC_AUTH_TOKEN
  API格式:    Anthropic Message（原生）
  API Key:    sk-你的密钥
  模型映射:   Opus / Sonnet / Haiku → deepseek-v4-pro
  启用 → 健康检查通过
```

### 3. 克隆项目，启动 Claude
```bash
git clone https://github.com/zq30330238/my-first-site30.git d:/AI网站文件夹
cd d:/AI网站文件夹
claude
```
对 Claude 说：**"运行 recover.py 恢复项目"**

---

## Claude 接管后自动完成
Python、Git、Node.js 安装 → pip 依赖 → Codex CLI → 代理配置 → 记忆恢复 → 全站验证
