# 渣哥任务清单 — 2026-05-26

## 任务1：重新下载65张错误图片（最高优先级）

### 背景
download_images.py 已修复——删除了 quick_validate 绕过豆包的逻辑，每张图必须豆包说YES才存盘。用它重新下载 image_mismatch_report.md 里标记的65张错图。

### 执行

1. 读取 `d:\AI网站文件夹\image_mismatch_report.md`，提取每张错图的"文件名"和"所属站点"

2. 从文件名推导角色名：
   - `hinata-hyuga_2.png` → 角色名 `hinata-hyuga`
   - `android18.png` → 角色名 `android-18`（加连字符）
   - `bardock-dbs.png` → 角色名 `bardock`
   - 去掉 `_2`/`_3` 后缀

3. 对每个角色跑：
   ```bash
   cd "d:\AI网站文件夹"
   python shared/download_images.py --site <site-dir> --character <name>
   ```
   已修复的 download_images.py 会自动：下载 → 豆包验证 → 不合格丢弃重试 → 合格存盘。最多9次尝试。

4. 对 download_images.py 9次全失败的角色，用手动备用方案：
   - 浏览器搜 `"[角色名] [系列名] PNG render transparent"`
   - 找到正确图片后下载到临时目录
   - 跑豆包确认：`python shared/doubao_vision.py <临时图片路径> "Is this clearly [角色名] from [系列名]? Answer YES or NO."`
   - YES → 复制到站点 images/ 目录，文件名与错图一致
   - NO → 放弃，记录到失败清单

5. 验证：
   ```bash
   python shared/pre_commit_audit.py 2>&1 | grep "file missing"
   ```
   新增图片缺失应该为0。

### 铁律
**宁可没图，不要错图。** 豆包说NO的绝对不存盘。9次全失败的角色记录到 failed_images.json，等人工找图。

---

## 任务2：检查远程服务器图片管线

### 背景
本地 download_images.py 已修，但远程服务器(206.119.168.150)上的 collect_images_loop.py 也需要确认豆包验证达标。

### 执行

1. SSH到服务器检查 collect_images_loop.py：
   ```bash
   ssh root@206.119.168.150
   grep -n "verify_with_doubao\|quick_validate\|doubao_vision" /root/my-first-site30/shared/collect_images_loop.py
   ```

2. 确认：
   - 有 `verify_with_doubao()` 函数
   - 下载后调用了豆包验证
   - 验证不通过会丢弃重试
   - 不存在"预检通过就跳过豆包"的逻辑

3. 如果缺验证 → 把本地 download_images.py 的验证逻辑移植过去

---

## 任务3：跑 daily_articles.py 新周期

所有站点0 ERROR + 图片修好之后：
```bash
cd "d:\AI网站文件夹"
python shared/daily_articles.py
```

生成新文章后跑审计确认0 ERROR，提交部署。

---

## 完成后输出报告

格式：
```
=== 渣哥工作报告 2026-05-26 ===

任务1: 图片重下载
- 成功重下: X/65
- 豆包拒绝(pngwing无正确图): Y/65
- 备用方案下载: Z/65
- 最终仍失败(需人工): W/65

任务2: 服务器管线检查
- 状态: [已达标/已修复/待处理]

任务3: daily_articles
- 生成文章: N篇
- 审计: [0 ERROR / N ERROR]
```
