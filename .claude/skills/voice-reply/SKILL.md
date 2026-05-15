---
name: voice-reply
description: 语音回复技能。将AI的文字回复通过Windows TTS朗读出来。触发：用户说"语音回复"、"读出来"、"说中文"、"用语音"等。
---

# 语音回复技能

将文字回复转为语音朗读输出，使用 Windows 系统自带的中文 TTS 引擎。

## 触发条件

用户说以下关键词时，在文字回复后自动朗读：
- "语音回复"、"语音"
- "读出来"、"念一下"
- "说给我听"、"讲出来"

## 工作方式

1. 正常输出文字回复
2. 将回复内容保存到临时文件 `C:\Users\Administrator\AppData\Local\Temp\claude-speech.txt`
3. 执行 PowerShell TTS 脚本朗读

## TTS 脚本

朗读脚本位于: `.claude/skills/voice-reply/speak.ps1`

调用方式:
```powershell
powershell -ExecutionPolicy Bypass -File "d:\AI网站文件夹\.claude\skills\voice-reply\speak.ps1"
```

## 注意事项
- 使用 Windows 自带中文语音（Microsoft Huihui Desktop）
- 语速默认为 0，可根据需要调整为 -2（慢）到 2（快）
- 太长的回复（>500字）会自动分段朗读
- 技术英文术语不会翻译，保持原样

## 语音优化
- 代码块跳过不读
- 表格转为口语化表述
- 英文链接不读，只读描述文字
