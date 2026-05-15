# 新机器恢复指南

只需 3 步手动操作，其余 Claude 自动完成。

## 1. 安装前置软件
```
Python 3.10+  — https://python.org
Git           — https://git-scm.com
Node.js       — https://nodejs.org
Claude Code   — 按官方文档安装
```

## 2. 克隆项目
```bash
git clone https://github.com/zq30330238/my-first-site30.git d:/AI网站文件夹
```

## 3. 设置 API 密钥
```powershell
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-你的密钥', 'User')
```
重新打开终端使环境变量生效。

## 4. 让 Claude 接管
```bash
cd d:/AI网站文件夹
claude
```
对 Claude 说：**"运行 recover.py 恢复项目"**

Claude 会自动完成：Python 依赖安装、Codex CLI 安装、代理配置、记忆恢复、全站验证。
