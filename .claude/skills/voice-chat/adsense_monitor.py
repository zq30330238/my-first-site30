"""AdSense 自动监控 - 定时采集数据 + 趋势分析 + 优化建议"""
import json, os, time, urllib.request, ssl
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adsense_data.json")

# 7个子站配置
SITES = {
    "main": "jycsd.com",
    "healthy": "healthy.jycsd.com",
    "pets": "pets.jycsd.com",
    "home": "home.jycsd.com",
    "finance": "finance.jycsd.com",
    "tech": "tech.jycsd.com",
    "travel": "travel.jycsd.com"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"records": [], "last_update": None}

def save_data(data):
    data["last_update"] = datetime.now().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def manual_record(site_key, impressions, clicks, earnings, page_views):
    """手动录入一次数据（后续可对接API自动化）"""
    data = load_data()
    data["records"].append({
        "time": datetime.now().isoformat(),
        "site": site_key,
        "domain": SITES.get(site_key, site_key),
        "impressions": int(impressions),
        "clicks": int(clicks),
        "earnings": float(earnings),
        "page_views": int(page_views),
        "ctr": round(clicks / impressions * 100, 2) if impressions > 0 else 0,
        "rpm": round(earnings / impressions * 1000, 4) if impressions > 0 else 0
    })
    save_data(data)
    return {"ok": True, "recorded": len(data["records"])}

def analyze():
    """分析趋势并给出优化建议"""
    data = load_data()
    records = data["records"]
    if len(records) < 2:
        return {"status": "insufficient", "message": "需要至少2条记录才能分析"}

    # 按站点分组
    by_site = {}
    for r in records:
        site = r["site"]
        if site not in by_site:
            by_site[site] = []
        by_site[site].append(r)

    analysis = {}
    for site, recs in by_site.items():
        recs_sorted = sorted(recs, key=lambda x: x["time"])
        latest = recs_sorted[-1]
        if len(recs_sorted) >= 2:
            prev = recs_sorted[-2]
            ctr_change = round(latest["ctr"] - prev["ctr"], 2)
            rpm_change = round(latest["rpm"] - prev["rpm"], 4)
        else:
            ctr_change = 0
            rpm_change = 0

        # 评分和建议
        suggestions = []
        if latest["ctr"] < 0.5:
            suggestions.append("CTR过低，建议调整广告位置到内容中间或末尾")
        if latest["rpm"] < 1.0:
            suggestions.append("RPM偏低，考虑优化内容质量提升广告单价")
        if ctr_change < -0.1:
            suggestions.append("CTR下降，检查广告遮挡或页面加载速度")
        if latest["impressions"] < 100:
            suggestions.append("展示量不足，需要增加SEO推广或发布新文章")

        analysis[site] = {
            "domain": SITES.get(site, site),
            "latest": latest,
            "ctr_change": ctr_change,
            "rpm_change": rpm_change,
            "score": "good" if latest["ctr"] > 1.0 and latest["rpm"] > 2.0 else "ok" if latest["ctr"] > 0.3 else "needs_work",
            "suggestions": suggestions or ["数据表现正常，继续保持"]
        }

    return {"status": "ok", "sites": analysis, "total_records": len(records)}

def report():
    """生成可读报表"""
    result = analyze()
    if result["status"] == "insufficient":
        return result["message"]

    lines = ["AdSense 站点数据报表", "=" * 35]
    for site, info in result["sites"].items():
        l = info["latest"]
        emoji = {"good": "✅", "ok": "⚠️", "needs_work": "🔴"}.get(info["score"], "❓")
        lines.append(f"\n{emoji} {info['domain']}")
        lines.append(f"   展示:{l['impressions']}  点击:{l['clicks']}  CTR:{l['ctr']}%  RPM:${l['rpm']}  收入:${l['earnings']}")
        for s in info["suggestions"]:
            lines.append(f"   → {s}")
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "record":
        print(json.dumps(manual_record(*sys.argv[2:7]), ensure_ascii=False))
    elif cmd == "analyze":
        print(json.dumps(analyze(), ensure_ascii=False, indent=2))
    elif cmd == "report":
        print(report())
    else:
        print("Usage: record <site> <impressions> <clicks> <earnings> <page_views>")
        print("       analyze")
        print("       report")
