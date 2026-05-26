#!/usr/bin/env python3
import os, re, sys
from urllib.parse import urlparse

BASE_DIR = r"d:\AI网站文件夹"
SITE_DIRS = [
    "dragonball-site","naruto-site","onepiece-site","hxh-site",
    "tokyoghoul-site","aot-site","jjk-site","bleach-site",
    "minecraft-site","eldenring-site","fortnite-site","lol-site",
    "valorant-site","sao-site","games-site","anime-site","jojo-site",
    "sub-healthy","sub-pets","sub-home","sub-finance","sub-tech",
    "sub-travel","sub-auto","sub-moto","sub-food",
    "dailymedadvice","entertainment","rightsdaily","main-site"
]

SITE_DOMAIN_MAP = {
    "sub-healthy":"healthy.jycsd.com","sub-pets":"pets.jycsd.com",
    "sub-home":"home.jycsd.com","sub-finance":"finance.jycsd.com",
    "sub-tech":"tech.jycsd.com","sub-travel":"travel.jycsd.com",
    "sub-auto":"auto.jycsd.com","sub-moto":"moto.jycsd.com",
    "sub-food":"food.jycsd.com","dailymedadvice":"dailymedadvice.com",
    "entertainment":"entertainment.jycsd.com","rightsdaily":"rightsdaily.com",
    "main-site":"jycsd.com","dragonball-site":"dragonball.jycsd.com",
    "naruto-site":"naruto.jycsd.com","onepiece-site":"onepiece.jycsd.com",
    "hxh-site":"hxh.jycsd.com","tokyoghoul-site":"tokyoghoul.jycsd.com",
    "aot-site":"aot.jycsd.com","jjk-site":"jjk.jycsd.com",
    "bleach-site":"bleach.jycsd.com","minecraft-site":"minecraft.jycsd.com",
    "eldenring-site":"eldenring.jycsd.com","fortnite-site":"fortnite.jycsd.com",
    "lol-site":"lol.jycsd.com","valorant-site":"valorant.jycsd.com",
    "sao-site":"sao.jycsd.com","games-site":"games.jycsd.com",
    "anime-site":"anime.jycsd.com","jojo-site":"jojo.jycsd.com",
}

def find_html(site):
    fp = os.path.join(BASE_DIR, site)
    res = []
    for r, d, fs in os.walk(fp):
        for f in fs:
            if f.endswith(".html"):
                res.append(os.path.join(r, f))
    return sorted(res)

def audit(site):
    issues = []
    htmls = find_html(site)
    if not htmls:
        return [("WARN", "No HTML files found")]
    sitedir = os.path.join(BASE_DIR, site)
    exp_domain = SITE_DOMAIN_MAP.get(site, site + ".jycsd.com")
    for hf in htmls:
        sf = os.path.relpath(hf, BASE_DIR)
        with open(hf, "r", encoding="utf-8", errors="replace") as f:
            c = f.read()
        # og:image
        ogm = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']*)["\']', c, re.I)
        if ogm:
            ogv = ogm.group(1)
            if ogv.startswith("http"):
                od = urlparse(ogv).netloc.replace("www.","")
                ed = exp_domain.replace("www.","")
                if od != ed and not od.endswith("." + ed) and od != "jycsd.com":
                    issues.append(("FAIL", f"{sf}: og:image domain '{od}' != expected '{ed}'"))
            ws = re.search(r'(sub-\w+)\.jycsd\.com', ogv)
            if ws:
                w = ws.group(1)
                es = site if site.startswith("sub-") else None
                if es and w != es:
                    issues.append(("FAIL", f"{sf}: og:image wrong subdomain '{w}' vs '{es}'"))
        else:
            issues.append(("FAIL", f"{sf}: Missing og:image"))
        # canonical
        cm = re.search(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', c, re.I)
        if cm:
            cv = cm.group(1)
            if cv.startswith("http"):
                cd = urlparse(cv).netloc.replace("www.","")
                ed = exp_domain.replace("www.","")
                if cd != ed and not cd.endswith("." + ed):
                    issues.append(("FAIL", f"{sf}: canonical domain '{cd}' != expected '{ed}'"))
            ws = re.search(r'(sub-\w+)\.jycsd\.com', cv)
            if ws:
                w = ws.group(1)
                es = site if site.startswith("sub-") else None
                if es and w != es:
                    issues.append(("FAIL", f"{sf}: canonical wrong subdomain '{w}' vs '{es}'"))
        else:
            issues.append(("FAIL", f"{sf}: Missing canonical link"))
        # images
        for m in re.finditer(r'src=["\']([^"\']+)["\']', c):
            src = m.group(1)
            src_clean = src.split("?")[0].split("#")[0]
            if not src_clean:
                continue
            if src_clean.startswith("http"):
                ws = re.search(r'(sub-\w+)\.jycsd\.com', src_clean)
                if ws:
                    w = ws.group(1)
                    es = site if site.startswith("sub-") else None
                    if es and w != es:
                        issues.append(("FAIL", f"{sf}: img src wrong subdomain '{w}': {src_clean[:80]}"))
            elif not src_clean.startswith("//"):
                hdir = os.path.dirname(hf)
                ipath = os.path.normpath(os.path.join(hdir, src_clean))
                if not os.path.exists(ipath):
                    issues.append(("FAIL", f"{sf}: Image not found: {src}"))
        # internal dead links
        for m in re.finditer(r'href=["\']([^"\']+)["\']', c):
            h = m.group(1)
            hc = h.split("#")[0].split("?")[0]
            if not hc or hc.startswith("http") or hc.startswith("//") or hc.startswith("tel:") or hc.startswith("mailto:"):
                continue
            if hc.startswith("/"):
                t = os.path.normpath(os.path.join(sitedir, hc.lstrip("/")))
            else:
                t = os.path.normpath(os.path.join(os.path.dirname(hf), hc))
            if not os.path.exists(t):
                if os.path.isdir(t):
                    if not os.path.exists(os.path.join(t, "index.html")):
                        issues.append(("FAIL", f"{sf}: Link not found: {h}"))
                else:
                    issues.append(("FAIL", f"{sf}: Link not found: {h}"))
        # category-xxx.html dead links
        for m in re.finditer(r'href=["\']([^"\']*category-[^"\']*\.html)["\']', c):
            cl = m.group(1).split("#")[0].split("?")[0]
            if cl.startswith("http"):
                continue
            t = os.path.normpath(os.path.join(os.path.dirname(hf), cl))
            if not os.path.exists(t):
                issues.append(("FAIL", f"{sf}: Category link dead: {cl}"))
    seen = set()
    res = []
    for s, m in issues:
        k = (s, m)
        if k not in seen:
            seen.add(k)
            res.append((s, m))
    return res

def main():
    tf, tw = 0, 0
    allr = {}
    for site in SITE_DIRS:
        print(f"\n=== {site} ===", flush=True)
        iss = audit(site)
        allr[site] = iss
        fcnt = sum(1 for s,_ in iss if s=="FAIL")
        wcnt = sum(1 for s,_ in iss if s=="WARN")
        tf += fcnt; tw += wcnt
        print(f"  FAIL={fcnt} WARN={wcnt}")
        for s,m in iss:
            print(f"  [{s}] {m}")
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    print(f"Total FAIL: {tf}")
    print(f"Total WARN: {tw}")
    if tf:
        print("\n--- ALL FAILS ---")
        for site in SITE_DIRS:
            for s,m in allr[site]:
                if s=="FAIL":
                    print(f"[FAIL] {site}: {m}")
    print("\n--- PER-SITE ---")
    for site in SITE_DIRS:
        iss = allr.get(site,[])
        fcnt = sum(1 for s,_ in iss if s=="FAIL")
        wcnt = sum(1 for s,_ in iss if s=="WARN")
        st = "BLOCK" if fcnt else "PASS"
        print(f"[{st}] {site}: {fcnt} fails, {wcnt} warns")

if __name__=="__main__":
    main()
