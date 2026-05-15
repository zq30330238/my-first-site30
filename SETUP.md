# 新机器恢复指南

## 1. 前置软件
```bash
# Python 3.10+ (系统安装)
# Git (系统安装)
# Node.js (Codex CLI 需要)
```

## 2. 克隆项目
```bash
git clone <repo-url> d:/AI网站文件夹
cd d:/AI网站文件夹
```

## 3. 安装 Python 依赖
```bash
# Codex 代理
pip install flask waitress requests python-dotenv

# 语音系统（可选）
pip install vosk pyaudio websockets

# OCR（可选）
pip install easyocr pillow pyautogui
```

## 4. 安装 Codex CLI
```bash
npm i -g @openai/codex
```

## 5. 恢复配置文件

### Claude Code 设置 & 记忆
`settings.json` 含 API 密钥，不存 git。手动复制：
```
原文件: C:\Users\<旧用户名>\.claude\settings.json
目标:   C:\Users\<新用户名>\.claude\settings.json
```
复制 `backup-config/memory/` → `C:\Users\<用户名>\.claude\projects\d--AI-----\memory\`

### Codex 配置
复制 `backup-config/codex-config.toml` → `C:\Users\<用户名>\.codex\config.toml`

## 6. 设置环境变量
```powershell
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', '<你的API密钥>', 'User')
```

## 7. 配置 Codex 代理
```bash
cd d:/AI网站文件夹/.claude/codex-proxy
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxx
```

## 8. 验证
```bash
# 检查代理
curl http://127.0.0.1:5000/v1/models

# 检查 Codex
cd d:/AI网站文件夹
codex exec "echo hello"
```
