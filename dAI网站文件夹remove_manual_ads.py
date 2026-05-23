"""Remove all manual AdSense ad units from all sites on the server.
Keeps the head script tag (required for Auto Ads)."""
import subprocess, sys, re

sites = [
    'aot-site', 'blackclover-site', 'bleach-site', 'bluelock-site',
    'csm-site', 'deathnote-site', 'demonslayer-site', 'eldenring-site',
    'entertainment', 'fairytail-site', 'fma-site', 'fortnite-site',
    'gintama-site', 'haikyuu-site', 'hxh-site', 'jjk-site',
    'jojo-site', 'mha-site', 'minecraft-site', 'mobpsycho-site',
    'naruto-site', 'onepiece-site', 'opm-site', 'rezero-site',
    'sao-site', 'spyxfamily-site', 'steinsgate-site', 'tokyoghoul-site',
]

script = '''
import os, re

sites = {sites!r}
count = 0
for site in sites:
    path = f'/root/my-first-site30/{site}/index.html'
    if not os.path.exists(path):
        print(f'SKIP {site}: not found')
        continue
    with open(path, 'r') as f:
        content = f.read()
    original = content

    # Remove all <ins class="adsbygoogle"> ... </ins> + following <script> push()
    content = re.sub(
        r'<ins\s+class="adsbygoogle"[^>]*>.*?</ins>\s*<script>\(adsbygoogle.*?</script>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove leftover standalone <ins> or push scripts if any
    content = re.sub(
        r'<script>\(adsbygoogle.*?</script>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove commented-out ad placeholders like <!-- Ad: ... -->
    content = re.sub(r'<!--\s*Ad:.*?-->\s*', '', content, flags=re.DOTALL)

    # Clean up empty ad container divs
    content = re.sub(
        r'<div\s+class="[^"]*ad-container[^"]*"[^>]*>\s*</div>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        count += 1
        print(f'OK {site}: ads removed, size {len(content)}')
    else:
        print(f'NOCHANGE {site}')
print(f'Done: {count}/{len(sites)} sites modified')
'''

# Execute on server
ssh_cmd = f"ssh root@206.119.168.150 python3 << 'EOSERVER'\n{script}\nEOSERVER"
result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=60)
print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr[:500])
