"""Generate download tasks for missing ethnic clothing images and insert HTML."""
import os, json

pages_dir = r'd:\AI网站文件夹\clothing-site\chinese\56-ethnic-groups'
images_dir = r'd:\AI网站文件夹\clothing-site\images'

# Get list of ethnic groups missing male/female images
with open(os.path.join(pages_dir, 'han.html'), 'r', encoding='utf-8') as f:
    han_content = f.read()

tasks = []
ethnic_names = {}

for fname in sorted(os.listdir(pages_dir)):
    if fname == 'index.html' or not fname.endswith('.html'):
        continue
    ethnic = fname.replace('.html', '')
    if ethnic == 'han':
        continue

    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if male/female images are present
    has_male = f'{ethnic}_male' in content
    has_female = f'{ethnic}_female' in content

    # Get ethnic group display name from page title
    title_match = content[content.find('<title>'):content.find('</title>')]

    if not has_male:
        tasks.append({
            'query': f'{ethnic} Chinese ethnic minority traditional male clothing costume',
            'output': os.path.join(images_dir, f'{ethnic}_male.jpg'),
            'check': f'YES if this image shows traditional male clothing/costume of the {ethnic} ethnic group. NO if wrong ethnic group, wrong gender, or not traditional clothing.'
        })
    if not has_female:
        tasks.append({
            'query': f'{ethnic} Chinese ethnic minority traditional female clothing costume',
            'output': os.path.join(images_dir, f'{ethnic}_female.jpg'),
            'check': f'YES if this image shows traditional female clothing/costume of the {ethnic} ethnic group. NO if wrong ethnic group, wrong gender, or not traditional clothing.'
        })

    if not has_male or not has_female:
        ethnic_names[ethnic] = {'missing_male': not has_male, 'missing_female': not has_female}

with open(r'd:\AI网站文件夹\temp_ethnic_tasks.json', 'w', encoding='utf-8') as f:
    json.dump(tasks, f, indent=2)

print(f'Total tasks: {len(tasks)}')
print(f'Missing male: {sum(1 for t in tasks if "male" in t["output"])}')
print(f'Missing female: {sum(1 for t in tasks if "female" in t["output"])}')
print(f'Pages affected: {len(ethnic_names)}')
print('Tasks saved to temp_ethnic_tasks.json')
