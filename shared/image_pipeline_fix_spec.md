# 图片下载管线改造方案 — 豆包验证前置

## 核心改动

所有图片下载管线统一执行：
```
搜索URL → 下载 → 本地预检(尺寸/格式/MD5) → 豆包验证 → compress → 存盘
```

**豆包验证不合格 → 删除临时文件 → 换下一个候选URL → 所有候选用完换搜索词 → 直到通过。**

## 改哪个文件

### 1. shared/download_images.py（最高优先级）

**问题**：`verify_character()` 函数里，`quick_validate()` 预检通过后直接 return True，不调豆包。一个尺寸合格但内容错误的图片（比如 dragonball-site 的 android18.png 存的是中国龙）就这样通过了。

**改法**：
- 删除 `quick_validate()` 预检通过即返回 True 的逻辑
- 改为：下载 → quick_validate 仅做格式/尺寸/MD5过滤（不通过就丢弃） → 必须调豆包验证 → 豆包说YES才存盘
- 用管线B的 prompt 模板（见下方）
- 验证不通过自动重试下一个候选URL
- 所有候选URL用完还不通过 → 换搜索词（在角色名后加 "anime render" / "character art" / "official art"）

### 2. shared/collect_content_images.py

**问题**：Unsafe fallback 不经过豆包验证就保存。

**改法**：
- Unsplash fallback 也走豆包验证
- 增强验证 prompt（从 "Is this image about 'TITLE'?" 改为含判断标准的版本）

### 3. 统一验证 prompt 模板

```python
VERIFY_PROMPT = """Look at this image carefully. 
Character/Subject expected: {character_name}
Context: {series_or_topic}

Answer YES if ALL of these are true:
1. This image CLEARLY shows {character_name}
2. The character/subject is recognizable and matches common depictions
3. This is a proper character image or scene image (not a logo, text, or abstract pattern)

Answer NO if ANY of these is true:
1. This is a different character/person/subject entirely
2. This is a logo, text, chart, abstract pattern, or decorative frame
3. This is a group/crowd shot where the specific character can't be identified
4. The image is too blurry/dark to identify the subject
5. This is a real-life cosplay photo (not the actual animated/game character)

Reply ONLY with YES or NO."""
```

### 4. 重试机制

```
每个角色: 最多3个候选URL × 最多3组搜索词 = 最多9次尝试
搜索词迭代: 
  "{character} {series} render PNG" 
  → "{character} {series} official art" 
  → "{character} anime character transparent"
  
全部失败 → 记录到 failed_images.json，人工介入
```

## 验证命令（改完后自测）

```bash
# 下载一张已知会失败的图片验证流程能正确拒绝
cd "d:\AI网站文件夹"
python shared/download_images.py --site dragonball-site --character android-18 --dry-run
# 预期：豆包拒绝"中国龙"图片 → 自动重试 → 找到正确图片或记录失败
```

## 不改的文件
- shared/doubao_vision.py — 核心API封装没问题
- shared/collect_images_loop.py — 已有较完善的验证，只统一prompt即可
- shared/sync_collected.py — 纯文件同步
