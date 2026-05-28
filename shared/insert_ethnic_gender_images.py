"""Insert male and female <figure> blocks into unfixed ethnic group pages."""
import os, re

pages_dir = r'd:\AI网站文件夹\clothing-site\chinese\56-ethnic-groups'

ethnic_display_names = {
    'achang': 'Achang', 'bai': 'Bai', 'blang': 'Blang', 'bonan': 'Bonan',
    'buyei': 'Buyei', 'dai': 'Dai', 'daur': 'Daur', 'deang': 'De\'ang',
    'derung': 'Derung', 'dong': 'Dong', 'dongxiang': 'Dongxiang', 'evenki': 'Evenki',
    'gaoshan': 'Gaoshan', 'gelao': 'Gelao', 'gin': 'Gin',
    'hani': 'Hani', 'hezhen': 'Hezhen', 'hui': 'Hui',
    'jingpo': 'Jingpo', 'jino': 'Jino', 'kazakh': 'Kazakh', 'korean': 'Korean',
    'kyrgyz': 'Kyrgyz', 'lahu': 'Lahu', 'lhoba': 'Lhoba', 'li': 'Li',
    'lisu': 'Lisu', 'manchu': 'Manchu', 'maonan': 'Maonan', 'miao': 'Miao',
    'monba': 'Monba', 'mongolian': 'Mongolian', 'mulao': 'Mulao',
    'naxi': 'Naxi', 'nu': 'Nu', 'orogen': 'Orogen', 'pumi': 'Pumi',
    'qiang': 'Qiang', 'russian': 'Russian', 'salar': 'Salar', 'she': 'She',
    'shui': 'Shui', 'tajik': 'Tajik', 'tatar': 'Tatar', 'tibetan': 'Tibetan',
    'tu': 'Tu', 'tujia': 'Tujia', 'uyghur': 'Uyghur', 'uzbek': 'Uzbek',
    'va': 'Va', 'xibe': 'Xibe', 'yao': 'Yao', 'yi': 'Yi', 'yugur': 'Yugur',
    'zhuang': 'Zhuang',
}

male_fig_template = '''            <figure class="my-8">
                <img src="/images/{ethnic}_male.jpg" alt="{display} male traditional clothing and headwear" loading="lazy" class="w-full rounded-lg">
                <figcaption class="text-sm text-gray-500 mt-2 text-center">{display} male traditional attire — distinctive garments, headwear, and accessories worn by men of this ethnic group.</figcaption>
            </figure>'''

female_fig_template = '''            <figure class="my-8">
                <img src="/images/{ethnic}_female.jpg" alt="{display} female traditional clothing and silver ornaments" loading="lazy" class="w-full rounded-lg">
                <figcaption class="text-sm text-gray-500 mt-2 text-center">{display} female traditional attire — embroidered garments, silver jewelry, and headdresses characteristic of this ethnic group.</figcaption>
            </figure>'''

changed = 0
for fname in sorted(os.listdir(pages_dir)):
    if fname == 'index.html' or not fname.endswith('.html'):
        continue
    ethnic = fname.replace('.html', '')
    if ethnic == 'han':
        continue
    if ethnic not in ethnic_display_names:
        continue

    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    has_male = f'{ethnic}_male' in content
    has_female = f'{ethnic}_female' in content
    if has_male and has_female:
        continue

    display = ethnic_display_names[ethnic]
    new_content = content

    # Insert male figure before first <figure class="my-8"> (the detail image)
    if not has_male:
        first_fig = new_content.find('<figure class="my-8">')
        if first_fig != -1:
            male_html = male_fig_template.format(ethnic=ethnic, display=display)
            new_content = new_content[:first_fig] + male_html + '\n\n' + new_content[first_fig:]

    # Insert female figure after </blockquote>
    if not has_female:
        bq_end = new_content.find('</blockquote>')
        if bq_end != -1:
            bq_real_end = new_content.find('\n', bq_end) + 1
            female_html = female_fig_template.format(ethnic=ethnic, display=display)
            new_content = new_content[:bq_real_end] + '\n' + female_html + '\n' + new_content[bq_real_end:]

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    changed += 1
    print(f'  Fixed: {fname}')

print(f'Total pages modified: {changed}')
