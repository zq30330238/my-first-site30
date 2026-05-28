import os
import re
import time
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("C:/Users/Administrator/.claude/projects/d--AI-----/memory")
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
NOW = time.time()

def get_mtime_days(path):
    return (NOW - os.path.getmtime(path)) / 86400

def read_file(path):
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''

def has_origin_session_id(content):
    fm_end = content.find('---', 3)
    if fm_end == -1:
        fm_end = 500
    header = content[:fm_end]
    return bool(re.search(r'originSessionId:\s*\S+', header))

def extract_memory_index_refs():
    text = read_file(MEMORY_INDEX)
    refs = set()
    for m in re.finditer(r'\]\(([^)]+\.md)\)', text):
        refs.add(m.group(1))
    return refs

def check_staleness(files):
    buckets = {'<30d': [], '30-90d': [], '90-180d': [], '>180d': []}
    no_origin = []
    for fpath in files:
        days = get_mtime_days(fpath)
        fname = fpath.name
        mt = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d')
        content = read_file(fpath)
        if not has_origin_session_id(content):
            no_origin.append(fname)
        if days < 30:
            buckets['<30d'].append(fname)
        elif days < 90:
            buckets['30-90d'].append(fname)
        elif days < 180:
            buckets['90-180d'].append((fname, mt))
        else:
            buckets['>180d'].append((fname, mt))
    return buckets, no_origin

def extract_short_text(text):
    fm_end = text.find('---', 3)
    if fm_end == -1:
        fm_end = 0
    body = text[fm_end + 3:]
    desc_match = re.search(r'description:\s*(.+)', text[:min(fm_end + 100, 2000)])
    desc = desc_match.group(1).strip().lower() if desc_match else ''
    title_match = re.search(r'^#\s+(.+)', body, re.MULTILINE)
    title = title_match.group(1).strip().lower() if title_match else ''
    return desc + ' ' + title

def check_contradictions(files):
    known_pairs = [
        ('feedback_ai_generated_images_only.md',
         'feedback_free_images_not_generated.md',
         '"must use Seedream" vs "must download from free sources"'),
        ('project_global_ad_requirements.md',
         'feedback_template_generation_checklist.md',
         '"manual ads" vs "auto ads only"'),
    ]
    results = []
    for f1, f2, desc in known_pairs:
        p1 = MEMORY_DIR / f1
        p2 = MEMORY_DIR / f2
        if p1.exists() and p2.exists():
            results.append((f1, f2, desc))

    short_map = {}
    for fpath in files:
        if fpath.name == 'MEMORY.md':
            continue
        short_map[fpath.name] = extract_short_text(read_file(fpath))

    opposing_keywords = [
        (['seedream', 'ai生成', 'ai generated'], ['unsplash', 'pexels', 'free download']),
    ]
    for set_a, set_b in opposing_keywords:
        found_a = set()
        found_b = set()
        for fname, short_text in short_map.items():
            if any(kw in short_text for kw in set_a):
                found_a.add(fname)
            if any(kw in short_text for kw in set_b):
                found_b.add(fname)
        both = found_a & found_b
        for f in both:
            found_a.discard(f)
            found_b.discard(f)
        for fa in sorted(found_a):
            for fb in sorted(found_b):
                if fa < fb:
                    if not any(p[0] == fa and p[1] == fb for p in results):
                        results.append((fa, fb, None))
    return results

def check_orphans(files):
    refs = extract_memory_index_refs()
    orphans = []
    for fpath in files:
        if fpath.name == 'MEMORY.md':
            continue
        if fpath.name not in refs:
            orphans.append(fpath.name)
    return sorted(orphans)

def main():
    all_md = sorted(MEMORY_DIR.glob('*.md'))
    print(f'=== Rule Health Check {datetime.now().strftime("%Y-%m-%d %H:%M")} ===')
    print(f'  Memory directory: {MEMORY_DIR}')
    print(f'  Total .md files: {len(all_md)}')
    print()

    buckets, no_origin = check_staleness(all_md)
    print('--- Staleness ---')
    for label in ['<30d', '30-90d', '90-180d', '>180d']:
        items = buckets[label]
        count = len(items)
        if label in ('<30d', '30-90d'):
            print(f'  {label}: {count} files')
        else:
            tag = '[STALE]' if label == '90-180d' else '[VERY STALE]'
            print(f'  {label}: {count} files {tag}')
            for fname, mtime in items:
                print(f'    {fname} (last modified {mtime})')
    if no_origin:
        print(f'\n  No originSessionId ({len(no_origin)} files):')
        for fname in sorted(no_origin):
            print(f'    {fname}')

    contradictions = check_contradictions(all_md)
    print('\n--- Potential Contradictions ---')
    if contradictions:
        for f1, f2, desc in contradictions:
            print(f'  {f1} vs {f2}')
            if desc:
                print(f'    {desc}')
        print('  -> Human review needed')
    else:
        print('  None detected')

    orphans = check_orphans(all_md)
    print('\n--- Orphan Rules (not in MEMORY.md) ---')
    if orphans:
        for fname in orphans:
            print(f'  {fname}')
    else:
        print('  None found')

    stale_count = len(buckets['90-180d']) + len(buckets['>180d'])
    contra_count = len(contradictions)
    orphan_count = len(orphans)
    print(f'\n--- Summary ---')
    print(f'  {stale_count} stale, {contra_count} contradiction pairs, {orphan_count} orphans')

if __name__ == '__main__':
    main()
