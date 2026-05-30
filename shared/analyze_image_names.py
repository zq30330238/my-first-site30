"""Analyze image filename vs page name matching for confirmed mismatches"""
import json, os

r = json.load(open('d:/AI网站文件夹/visual_audit_verified.json', 'r', encoding='utf-8'))
confirmed = r['confirmed']

img_matches = 0
img_mismatches = 0
character_pages = 0
category_pages = 0
index_pages = 0

for m in confirmed:
    page = m['page'].replace('\\', '/')
    img = m['image'].split('/')[-1] if m['image'] else ''
    page_name = page.split('/')[-1].replace('.html', '')

    # Classify page type
    is_index = page_name == 'index'
    is_category = any(x in page for x in ['/techniques/', '/sagas/', '/races/', '/transformations/',
                                            '/weapons/', '/gear/', '/nen/', '/hunter-association/',
                                            '/parts/', '/arcs/', '/breathing/', '/elements/'])

    if is_index:
        index_pages += 1
    elif is_category:
        category_pages += 1
    else:
        character_pages += 1

    # Check image name match
    if img.startswith(page_name):
        img_matches += 1
    else:
        img_mismatches += 1
        # Determine severity
        if is_index:
            severity = 'LOW (index page, generic image ok)'
        elif is_category:
            severity = 'MEDIUM (category page may benefit from better image)'
        else:
            # Check if correct image exists
            site_dir = f'd:/AI网站文件夹/{m["site"]}'
            expected_img = f'{page_name}.png'
            expected_path = os.path.join(site_dir, 'images', expected_img)
            if os.path.exists(expected_path):
                severity = 'HIGH — correct image EXISTS but not used!'
            else:
                severity = 'HIGH — correct image MISSING, needs generation'
        print(f'  [{severity}] {m["site"]}/{page}')
        print(f'    Title: {m["title"][:70]}')
        print(f'    Image: {img}  (expected: {page_name}.png)')
        print()

print(f'=== SUMMARY ===')
print(f'Total confirmed: {len(confirmed)}')
print(f'  Character pages: {character_pages}')
print(f'  Category pages (tech/saga/race/trans/weapon/etc): {category_pages}')
print(f'  Index pages: {index_pages}')
print(f'Image name matches page: {img_matches}')
print(f'Image name DOES NOT match: {img_mismatches}')
