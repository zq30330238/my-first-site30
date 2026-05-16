"""One-shot: add GA4 tracking code to all HTML pages"""
from pathlib import Path

GA4_CODE = '''<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-GGNWR1X1GV');
</script>'''

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

count = 0
for d in DIRS:
    for f in sorted((ROOT / d).glob('*.html')):
        html = f.read_text(encoding='utf-8')
        if 'G-GGNWR1X1GV' in html:
            continue
        # Insert GA4 before </head>
        html = html.replace('</head>', GA4_CODE + '\n</head>')
        f.write_text(html, encoding='utf-8')
        count += 1

print(f'Added GA4 to {count} pages')
