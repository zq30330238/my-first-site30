"""
通用 Related Characters/Items 旋转脚本
支持两种格式: scroll-snap-x (aot/onepiece/naruto等) 和 grid (bleach/jjk等)
用法: python shared/rotate_related.py <site_dir> <subdir> [--count 5] [--dry-run]
"""
import os, re, sys, random, argparse
from collections import OrderedDict

def extract_char_data(filepath, subdir):
    """从HTML文件提取角色数据"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    fname = os.path.basename(filepath)
    slug = fname.replace('.html', '')

    # 提取名称 (h1)
    m = re.search(r'<h1[^>]*class="[^"]*font-black[^"]*"[^>]*>(.+?)</h1>', content)
    if not m:
        m = re.search(r'<h1[^>]*class="[^"]*font-bold[^"]*"[^>]*>(.+?)</h1>', content)
    if not m:
        m = re.search(r'<h1[^>]*>(.+?)</h1>', content)
    name = m.group(1).strip() if m else slug.replace('-', ' ').title()

    # 提取副标题 — 多种格式
    m = re.search(r'<span class="[^"]*rounded-full[^"]*"[^>]*>(.+?)</span>', content)
    if not m:
        m = re.search(r'<p class="[^"]*text-(?:lg|sm)[^"]*">([^<]+)</p>', content)
    subtitle = m.group(1).strip() if m else ''

    # 提取主图
    m = re.search(r'<img src="(/images/[^"]+\.(?:png|jpg|jpeg|webp))"', content)
    img = m.group(1) if m else f'/images/{slug}.png'

    # 提取hover ring颜色 (grid格式)
    m = re.search(r'hover:ring-\[(#[^\]]+)\]', content)
    accent_color = m.group(1) if m else None

    # 提取border-color (scroll格式)
    m = re.search(r"border-color:([#\w]+)", content)
    border_color = m.group(1) if m else '#374151'

    # 提取bg class
    m = re.search(r'aspect-square (bg-[\w\[\]#]+)', content)
    bg_class = m.group(1) if m else 'bg-bgPrimary'

    return {
        'slug': slug,
        'name': name,
        'subtitle': subtitle,
        'img': img,
        'url': f'/{subdir}/{slug}.html',
        'accent_color': accent_color,
        'border_color': border_color,
        'bg_class': bg_class,
    }

def detect_format(filepath):
    """检测站点使用的格式: 'scroll' 或 'grid'"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if 'scroll-snap-x' in content:
        return 'scroll'
    if 'grid grid-cols-2' in content:
        return 'grid'
    return None

def build_scroll_card(c, template=None):
    """构建scroll-snap-x格式卡片"""
    return (
        f'<div class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex-shrink-0 w-40"'
        f' style="border-color:{c["border_color"]}">\n'
        f'<a href="{c["url"]}" class="block">\n'
        f'<div class="w-full aspect-square {c["bg_class"]} overflow-hidden flex items-center justify-center">'
        f'<img src="{c["img"]}" alt="{c["name"]} — {c["subtitle"]}"'
        f' title="{c["name"]}" class="w-full h-full object-cover"'
        f' style="object-position:center top" loading="eager"></div>\n'
        f'<div class="p-3 text-center">\n'
        f'<h4 class="font-bold text-sm">{c["name"]}</h4>\n'
        f'<p class="text-xs text-textSecondary mt-0.5">{c["subtitle"]}</p>\n'
        f'</div>\n</a>\n</div>'
    )

def build_grid_card(c):
    """构建grid格式卡片"""
    accent = c.get('accent_color', '#f39c12')
    return (
        f'<a href="{c["url"]}" class="bg-[#161b22] rounded-lg overflow-hidden hover:ring-2 hover:ring-[{accent}] transition-all duration-300">\n'
        f'    <div class="aspect-square bg-gray-800 relative overflow-hidden">\n'
        f'        <img src="{c["img"]}" alt="{c["name"]}" class="w-full h-full object-contain" loading="lazy" onerror="this.src=\'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22400%22><rect fill=%22%23161b22%22 width=%22400%22 height=%22400%22/><text fill=%22%23f39c12%22 font-size=%2220%22 x=%2250%%22 y=%2250%%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22>Bleach</text></svg>\'">\n'
        f'    </div>\n'
        f'    <div class="p-4">\n'
        f'        <h3 class="font-bold text-lg text-white">{c["name"]}</h3>\n'
        f'        <p class="text-sm text-gray-400">{c["subtitle"]}</p>\n'
        f'    </div>\n'
        f'</a>'
    )

def rotate_related(site_dir, subdir, card_count=5, dry_run=False):
    chars_dir = os.path.join(site_dir, subdir)
    if not os.path.isdir(chars_dir):
        print(f'ERROR: {chars_dir} not found')
        return False

    html_files = sorted([
        f for f in os.listdir(chars_dir)
        if f.endswith('.html') and f != 'index.html'
    ])

    if len(html_files) < card_count + 1:
        print(f'SKIP: only {len(html_files)} files, need at least {card_count + 1}')
        return False

    # 检测格式
    first_file = os.path.join(chars_dir, html_files[0])
    fmt = detect_format(first_file)
    if not fmt:
        print(f'ERROR: unknown format in {first_file}')
        return False
    print(f'Detected format: {fmt}')

    # 提取所有角色数据
    chars = OrderedDict()
    for fname in html_files:
        fp = os.path.join(chars_dir, fname)
        chars[fname] = extract_char_data(fp, subdir)

    if fmt == 'scroll':
        # scroll格式: 匹配 <h2>Related...</h2> <div class="scroll-snap-x..."> ... </div></div></div>
        section_re = re.compile(
            r'(<h2 class="[^"]*">Related \w+</h2>\s*<div class="scroll-snap-x[^"]*">).*?'
            r'(</div>\s*</div>\s*</div>)',
            re.DOTALL
        )
        build_fn = build_scroll_card
    else:
        # grid格式: 匹配 <section>...<h2>Related...</h2> <div class="grid..."> ... </div></section>
        section_re = re.compile(
            r'(<section class="[^"]*">\s*<h2 class="[^"]*">Related \w+</h2>\s*<div class="grid[^"]*">).*?'
            r'(</div>\s*</section>)',
            re.DOTALL
        )
        build_fn = build_grid_card

    modified = 0
    for i, (fname, char_data) in enumerate(chars.items()):
        fp = os.path.join(chars_dir, fname)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 旋转选择相关角色
        all_slugs = list(chars.keys())
        idx = all_slugs.index(fname)
        related = []
        for j in range(1, len(all_slugs)):
            ridx = (idx + j) % len(all_slugs)
            rname = all_slugs[ridx]
            rchar = chars[rname]
            if rname != fname and rchar not in related:
                related.append(rchar)
            if len(related) >= card_count:
                break

        cards_html = '\n'.join(build_fn(c) for c in related)

        m = section_re.search(content)
        if not m:
            print(f'WARN: {fname} — cannot find Related section pattern')
            continue

        replacement = m.group(1) + '\n' + cards_html + '\n' + m.group(2)
        new_content = content[:m.start()] + replacement + content[m.end():]

        if not dry_run:
            with open(fp, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(new_content)

        modified += 1

    print(f'{"[DRY RUN] " if dry_run else ""}{site_dir}/{subdir}: {modified}/{len(html_files)} files rotated')
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site_dir')
    parser.add_argument('subdir')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    rotate_related(args.site_dir, args.subdir, args.count, args.dry_run)
