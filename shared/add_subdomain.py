"""Add subdomains to DNSPod + create CF Pages projects + bind custom domains."""
import subprocess, json, sys, time, os

TENCENT_ID = "AKID9O2bzLj185tUxIUZWYjqJdqtlQuFTXgv"
TENCENT_KEY = "Ln7OSKzR3nXPH5qeYO6ld0tcFvTr44rS"
CF_API_TOKEN = "cfat_zx4dbsfmTXoWaChJF5lAnmc7EptnvCgOskiMPZGcda27a93f"
CF_ACCOUNT_ID = "4e8cd083c07627f679dd86dc5b488fb0"
DOMAIN = "jycsd.com"

# Phase 1: tonight
PHASE_1 = [
    ("games", "games-jycsd"),
    ("minecraft", "minecraft-jycsd"),
]

# Phase 2: this week
PHASE_2 = [
    ("eldenring", "eldenring-jycsd"),
    ("gta6", "gta6-jycsd"),
    ("lol", "lol-jycsd"),
    ("dragonball", "dragonball-jycsd"),
    ("anime", "anime-jycsd"),
]

# Full list for future
PHASE_ALL = PHASE_1 + PHASE_2 + [
    ("fortnite", "fortnite-jycsd"),
    ("valorant", "valorant-jycsd"),
    ("hogwartslegacy", "hogwartslegacy-jycsd"),
    ("terraria", "terraria-jycsd"),
    ("palworld", "palworld-jycsd"),
    ("bg3", "bg3-jycsd"),
    ("cyberpunk2077", "cyberpunk2077-jycsd"),
    ("valheim", "valheim-jycsd"),
    ("cs2", "cs2-jycsd"),
    ("apex", "apex-jycsd"),
    ("genshin", "genshin-jycsd"),
    ("hsr", "hsr-jycsd"),
    ("pokemon", "pokemon-jycsd"),
    ("zelda", "zelda-jycsd"),
    ("onepiece", "onepiece-jycsd"),
    ("naruto", "naruto-jycsd"),
    ("demonslayer", "demonslayer-jycsd"),
    ("jujutsukaisen", "jujutsukaisen-jycsd"),
    ("aot", "aot-jycsd"),
    ("mha", "mha-jycsd"),
    ("sololeveling", "sololeveling-jycsd"),
    ("frieren", "frieren-jycsd"),
    ("chainsawman", "chainsawman-jycsd"),
    ("deathnote", "deathnote-jycsd"),
    ("fma", "fma-jycsd"),
    ("eva", "eva-jycsd"),
    ("bebop", "bebop-jycsd"),
    ("tools", "tools-jycsd"),
    ("ghibli", "ghibli-jycsd"),
    ("prdbuilder", "prdbuilder-jycsd"),
]


def add_dns_record(subdomain, project_name):
    """Add CNAME record via Tencent Cloud DNSPod SDK."""
    from tencentcloud.common import credential
    from tencentcloud.dnspod.v20210323 import dnspod_client, models

    cred = credential.Credential(TENCENT_ID, TENCENT_KEY)
    client = dnspod_client.DnspodClient(cred, "")

    # Check if record already exists
    list_req = models.DescribeRecordListRequest()
    list_req.Domain = DOMAIN
    list_req.Limit = 200
    try:
        existing = client.DescribeRecordList(list_req)
        for r in existing.RecordList:
            if r.Name == subdomain:
                print(f"  [SKIP] DNS Record {subdomain}.{DOMAIN} already exists → {r.Value}")
                return True
    except Exception:
        pass  # No records matching subdomain filter → proceed to create

    # Create CNAME record
    req = models.CreateRecordRequest()
    req.Domain = DOMAIN
    req.SubDomain = subdomain
    req.RecordType = "CNAME"
    req.RecordLine = "默认"
    req.Value = f"{project_name}.pages.dev"
    req.TTL = 600
    resp = client.CreateRecord(req)
    record_id = resp.RecordId
    print(f"  [OK] DNS Created: {subdomain}.{DOMAIN} → {project_name}.pages.dev (ID:{record_id})")
    return True


def create_cf_project(project_name):
    """Create Cloudflare Pages project with Direct Upload mode."""
    # Check if project already exists
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {CF_API_TOKEN}",
         f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/pages/projects/{project_name}"],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    if data.get("success") and data.get("result", {}).get("name") == project_name:
        print(f"  [SKIP] CF Project {project_name} already exists")
        return True

    # Create project
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", f"Authorization: Bearer {CF_API_TOKEN}",
         "-H", "Content-Type: application/json",
         f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/pages/projects",
         "-d", json.dumps({"name": project_name, "production_branch": "main"})],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    if data.get("success"):
        print(f"  [OK] CF Project created: {project_name}.pages.dev")
        return True
    else:
        print(f"  [ERROR] CF Project creation failed: {data.get('errors', data)}")
        return False


def add_cf_custom_domain(project_name, subdomain):
    """Add custom domain to Cloudflare Pages project."""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", f"Authorization: Bearer {CF_API_TOKEN}",
         "-H", "Content-Type: application/json",
         f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/pages/projects/{project_name}/domains",
         "-d", json.dumps({"domain": f"{subdomain}.{DOMAIN}"})],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    if data.get("success"):
        print(f"  [OK] CF Domain bound: {subdomain}.{DOMAIN} → {project_name}")
        return True
    elif any("already exists" in str(e) for e in data.get("errors", [])):
        print(f"  [SKIP] CF Domain {subdomain}.{DOMAIN} already bound")
        return True
    else:
        print(f"  [ERROR] CF Domain binding: {data.get('errors', data)}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_subdomain.py <phase1|phase2|all|add <sub> <project>>")
        print(f"  phase1: {len(PHASE_1)} records (tonight)")
        print(f"  phase2: {len(PHASE_2)} more records (this week)")
        print(f"  all: {len(PHASE_ALL)} total records")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "phase1":
        targets = PHASE_1
    elif cmd == "phase2":
        targets = PHASE_2
    elif cmd == "all":
        targets = PHASE_ALL
    elif cmd == "add" and len(sys.argv) >= 4:
        targets = [(sys.argv[2], sys.argv[3])]
    else:
        print("Unknown command")
        sys.exit(1)

    print(f"Processing {len(targets)} subdomains...")
    for subdomain, project_name in targets:
        print(f"\n{subdomain}.{DOMAIN}:")
        try:
            add_dns_record(subdomain, project_name)
            create_cf_project(project_name)
            add_cf_custom_domain(project_name, subdomain)
            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERROR] {e}")

    # Verify
    print(f"\n{'='*50}")
    print("DNS propagation may take 1-5 minutes.")
    print("Verify in browser: https://{}.{}".format(targets[0][0], DOMAIN))


if __name__ == "__main__":
    main()
