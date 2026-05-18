"""
每日广告收益监控 —— 自动运行（nightly_worker 调用或独立执行）

前置条件:
  export GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
  export GOOGLE_CLIENT_SECRET="GOCSPX-xxx"
  export GOOGLE_REFRESH_TOKEN="1//xxx"          # 由 ad_auth.py 获取
  export ADSENSE_ACCOUNT_ID="pub-2595917642864488"  # 可选，默认值

无 Refresh Token 时静默跳过（exit 0），不影响其他阶段。
输出: logs/ad_report.json
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "logs" / "ad_report.json"

# 已知广告单元ID → 类型映射（ca-pub-2595917642864488 账户下）
AD_UNIT_TYPE_MAP = {
    "9112825459": "leaderboard",
    "4397738132": "halfpage",
    "9739511410": "billboard",
}

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
log = logging.getLogger("ad_monitor")


def get_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/adsense.readonly"],
    )
    return build("adsense", "v2", credentials=creds, cache_discovery=False)


def get_account():
    pub_id = os.environ.get("ADSENSE_ACCOUNT_ID", "pub-2595917642864488")
    return f"accounts/{pub_id}"


def api_call(service, account, date_range, dimensions, metrics):
    """通用 AdSense API v2 报告调用。"""
    body = {
        "reportingTimeZone": "ACCOUNT_TIME_ZONE",
        "dateRange": date_range,
        "dimensions": dimensions,
        "metrics": metrics,
    }
    return service.accounts().reports().generate(
        account=account, body=body
    ).execute()


def parse_rows(response, dimension_names, metric_names):
    """将 API 响应解析为 dict 列表。"""
    rows = []
    if "rows" not in response:
        return rows
    for row in response["rows"]:
        entry = {}
        for i, dim in enumerate(dimension_names):
            entry[dim] = row["dimensionValues"][i]["value"]
        for i, metric in enumerate(metric_names):
            val = row["metricValues"][i]["value"]
            entry[metric] = float(val) if val and val != "0.00" else 0.0
        entry["_raw"] = row
        rows.append(entry)
    return rows


def fetch_yesterday_total(service, account):
    """获取昨日总收益。"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    response = api_call(
        service, account,
        date_range="YESTERDAY",
        dimensions=[],
        metrics=["ESTIMATED_EARNINGS", "CLICKS", "IMPRESSIONS", "PAGE_VIEWS_RPM"],
    )
    if "rows" not in response or not response["rows"]:
        return {"earnings": 0.0, "clicks": 0, "impressions": 0, "rpm": 0.0}

    vals = response["rows"][0]["metricValues"]
    return {
        "earnings": float(vals[0]["value"]) if vals[0]["value"] else 0.0,
        "clicks": int(vals[1]["value"]) if vals[1]["value"] else 0,
        "impressions": int(vals[2]["value"]) if vals[2]["value"] else 0,
        "rpm": float(vals[3]["value"]) if vals[3]["value"] else 0.0,
    }


def fetch_by_ad_unit(service, account):
    """按广告单元获取昨日收益明细。"""
    response = api_call(
        service, account,
        date_range="YESTERDAY",
        dimensions=["AD_UNIT_NAME", "AD_UNIT_ID"],
        metrics=["ESTIMATED_EARNINGS", "CLICKS", "IMPRESSIONS"],
    )
    rows = parse_rows(response, ["AD_UNIT_NAME", "AD_UNIT_ID"],
                      ["ESTIMATED_EARNINGS", "CLICKS", "IMPRESSIONS"])

    by_unit = {}
    for row in rows:
        unit_id = row.get("AD_UNIT_ID", "unknown")
        short_id = unit_id.rsplit("::", 1)[-1] if "::" in unit_id else unit_id
        unit_type = AD_UNIT_TYPE_MAP.get(short_id, "unknown")
        by_unit[short_id] = {
            "earnings": row.get("ESTIMATED_EARNINGS", 0.0),
            "clicks": int(row.get("CLICKS", 0)),
            "impressions": int(row.get("IMPRESSIONS", 0)),
            "name": row.get("AD_UNIT_NAME", short_id),
            "type": unit_type,
        }
    return by_unit


def fetch_7day_trend(service, account):
    """获取最近7天每日收益用于趋势分析。"""
    response = api_call(
        service, account,
        date_range="LAST_7_DAYS",
        dimensions=["DATE"],
        metrics=["ESTIMATED_EARNINGS", "CLICKS", "IMPRESSIONS", "PAGE_VIEWS_RPM"],
    )
    return parse_rows(response, ["DATE"],
                      ["ESTIMATED_EARNINGS", "CLICKS", "IMPRESSIONS", "PAGE_VIEWS_RPM"])


def detect_trend(daily_data):
    """对比前7天，判断趋势。"""
    if len(daily_data) < 2:
        return "stable", []

    earnings = [d["ESTIMATED_EARNINGS"] for d in daily_data]
    today = earnings[-1] if earnings else 0
    yesterday = earnings[-2] if len(earnings) >= 2 else 0

    # 计算前6天均值（不含最新一天）
    prev = earnings[:-1]
    prev_avg = sum(prev) / len(prev) if prev else 0

    if prev_avg > 0:
        pct = (today - prev_avg) / prev_avg
    else:
        pct = 0

    if pct > 0.3:
        trend = "up"
    elif pct < -0.3:
        trend = "down"
    else:
        trend = "stable"

    alerts = []

    # 日环比暴跌检测
    if yesterday > 0 and today > 0:
        drop = (today - yesterday) / yesterday
        if drop < -0.3:
            alerts.append(f"Earnings dropped {abs(drop)*100:.0f}% vs previous day (${yesterday:.2f} → ${today:.2f})")

    # CTR 异常检测
    today_impressions = daily_data[-1].get("IMPRESSIONS", 0) if daily_data else 0
    today_clicks = daily_data[-1].get("CLICKS", 0) if daily_data else 0
    if today_impressions > 100 and today_clicks == 0:
        alerts.append("Zero clicks despite {0} impressions — possible ad serving issue".format(int(today_impressions)))

    # 持续下降检测（连续3天下降）
    if len(earnings) >= 4:
        last4 = earnings[-4:]
        if last4[0] > last4[1] > last4[2] > last4[3]:
            alerts.append("Earnings declining for 4 consecutive days")

    return trend, alerts


def run():
    # 优雅退出：无配置时静默跳过
    if not os.environ.get("GOOGLE_REFRESH_TOKEN"):
        log.info("Skipped: GOOGLE_REFRESH_TOKEN not set")
        return 0

    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        log.info("Skipped: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set")
        return 0

    service = get_service()
    account = get_account()

    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    log.info(f"获取 {report_date} AdSense 报告...")

    total = fetch_yesterday_total(service, account)
    by_unit = fetch_by_ad_unit(service, account)
    daily_data = fetch_7day_trend(service, account)
    trend, alerts = detect_trend(daily_data)

    report = {
        "date": report_date,
        "total": total,
        "by_ad_unit": by_unit,
        "daily_trend": [{"date": d["DATE"], "earnings": d["ESTIMATED_EARNINGS"],
                         "clicks": int(d.get("CLICKS", 0)),
                         "impressions": int(d.get("IMPRESSIONS", 0))}
                        for d in daily_data],
        "trend": trend,
        "alerts": alerts,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log.info(f"总收益: ${total['earnings']:.2f} | {total['clicks']} 点击 | {total['impressions']} 展示 | 趋势: {trend}")
    if alerts:
        for a in alerts:
            log.warning(f"异常: {a}")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(run())
