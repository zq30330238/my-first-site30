"""Add custom domains to CF Pages projects via API."""
import subprocess, json, os

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT = "4e8cd083c07627f679dd86dc5b488fb0"
BASE = "https://api.cloudflare.com/client/v4"

projects = [
    ("aot-jycsd", "aot.jycsd.com"),
    ("bleach-jycsd", "bleach.jycsd.com"),
    ("jjk-jycsd", "jjk.jycsd.com"),
    ("demonslayer-jycsd", "demonslayer.jycsd.com"),
    ("deathnote-jycsd", "deathnote.jycsd.com"),
    ("csm-jycsd", "csm.jycsd.com"),
    ("bluelock-jycsd", "bluelock.jycsd.com"),
    ("blackclover-jycsd", "blackclover.jycsd.com"),
    ("fairytail-jycsd", "fairytail.jycsd.com"),
    ("fma-jycsd", "fma.jycsd.com"),
    ("gintama-jycsd", "gintama.jycsd.com"),
    ("haikyuu-jycsd", "haikyuu.jycsd.com"),
    ("hxh-jycsd", "hxh.jycsd.com"),
    ("jojo-jycsd", "jojo.jycsd.com"),
    ("mha-jycsd", "mha.jycsd.com"),
    ("mobpsycho-jycsd", "mobpsycho.jycsd.com"),
    ("rezero-jycsd", "rezero.jycsd.com"),
    ("sao-jycsd", "sao.jycsd.com"),
    ("spyxfamily-jycsd", "spyxfamily.jycsd.com"),
    ("steinsgate-jycsd", "steinsgate.jycsd.com"),
    ("tokyoghoul-jycsd", "tokyoghoul.jycsd.com"),
    ("opm-jycsd", "opm.jycsd.com"),
    ("entertainment-jycsd", "entertainment.jycsd.com"),
]

ok = 0
fail = 0
for proj, domain in projects:
    body = json.dumps({"name": domain})
    cmd = f'curl -s -X POST "{BASE}/accounts/{ACCOUNT}/pages/projects/{proj}/domains' \
          f'" -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" -d \'{body}\''
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        if data.get("success"):
            print(f"OK: {domain}")
            ok += 1
        else:
            err = data.get("errors", [{}])[0].get("message", "unknown")
            if "already exists" in err:
                print(f"EXISTS: {domain}")
                ok += 1
            else:
                print(f"FAIL: {domain} → {err}")
                fail += 1
    except Exception as e:
        print(f"ERROR: {domain} → {e}")
        fail += 1

print(f"\nDone: {ok} added, {fail} failed")
