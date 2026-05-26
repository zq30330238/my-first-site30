---
name: deploy
description: 一键部署：git提交 + 推送 + wrangler部署全部7站到Cloudflare Pages
---

# 部署技能

修改文件后快速上线。git push 触发 CF Pages 自动部署，同时 wrangler 直接推送确保立即生效。

## 触发条件
- 用户说"部署"、"上线"、"发布"、"deploy"
- 用户说"推送"、"更新网站"
- 修改完文件需要上线

## 执行流程

### 1. 检查状态
```bash
git status
```

### 2. Git 提交推送
```bash
git add <changed-files>
git commit -m "<描述>"
git push origin master
```

### 3. Wrangler 部署所有站点
```bash
# CLOUDFLARE_API_TOKEN must be set in environment
export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN"

npx wrangler pages deploy main-site --project-name=main-site --branch=master

npx wrangler pages deploy sub-healthy --project-name=healthy-jycsd --branch=master
npx wrangler pages deploy sub-pets --project-name=pets-jycsd --branch=master
npx wrangler pages deploy sub-home --project-name=home-jycsd --branch=master
npx wrangler pages deploy sub-finance --project-name=finance-jycsd --branch=master
npx wrangler pages deploy sub-tech --project-name=tech-jycsd --branch=master
npx wrangler pages deploy sub-travel --project-name=travel-jycsd --branch=master
```

### 4. 验证
快速验证所有站点200：
```bash
for d in www healthy pets home finance tech travel; do
  curl -s -o /dev/null -w "%{http_code}" "https://$d.jycsd.com"
  echo " $d"
done
```

## 如果只改了某个子站
只部署该子站，跳过其他：
```bash
npx wrangler pages deploy sub-XXX --project-name=XXX-jycsd --branch=master
```
