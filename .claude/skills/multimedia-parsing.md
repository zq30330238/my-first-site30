---
name: multimedia-parsing
description: 图片/视频/抖音链接解析，通过豆包全模态API实现视觉和听觉理解
version: 1.0.0
source: git-history-analysis
---

# 多媒体解析（图/视频/音频）

## 工具

| 工具 | 用途 | 命令 |
|------|------|------|
| doubao_vision.py | 图片/截图/视频分析 | `python shared/doubao_vision.py <path>` |
| doubao_vision.py -s | 截图+分析 | `python shared/doubao_vision.py -s` |
| doubao_vision.py --video | 公网mp4分析 | `python shared/doubao_vision.py --video <url>` |
| douyin_parser.py | 抖音短链→解析 | `python shared/douyin_parser.py <链接>` |
| douyin_parser.py --video-file | 本地视频分析 | `python shared/douyin_parser.py --video-file <mp4>` |

## 抖音解析全链路

```
抖音短链 → 重定向提取视频ID → Chrome DevTools抓CDN地址 → 下载mp4 → base64 → 豆包解析
```

抖音CDN有Referer防盗链，豆包服务器无法直接访问。必须：
1. 本地下载（带 Referer: douyin.com）
2. base64 编码后直传

## 模型
- `doubao-seed-2-0-mini-260428` — 全模态，图+音+文
- API: `https://ark.cn-beijing.volces.com/api/v3`
- 不支持 v.douyin.com 短链，只认公网 mp4 或 base64 data URL
