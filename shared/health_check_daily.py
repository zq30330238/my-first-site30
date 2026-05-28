"""daily_articles.py health monitor.

Usage:
    python shared/health_check_daily.py              # Full report (all 4 checks)
    python shared/health_check_daily.py --quick       # Quick mode, skip quality check
    python shared/health_check_daily.py --cleanup     # Auto-kill zombies
    python shared/health_check_daily.py --quality     # Only content quality spot-check
"""

import csv
import io
import json
import random
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, date

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "shared" / "site_config.json"
PID_FILE = ROOT / ".claude" / "daily_pid.txt"
STATE_FILE = ROOT / "daily_articles_state.json"

EXPECTED_RUN_HOUR = 12
EXPECTED_MIN_ARTICLES = 33

TODAY = date.today()
NOW = datetime.now()


def get_running_pids():
    """Return set of PIDs for all running python.exe processes."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return set()

    pids = set()
    reader = csv.reader(io.StringIO(result.stdout))
    for row in reader:
        if len(row) >= 2 and row[1].strip().isdigit():
            pids.add(int(row[1].strip()))
    return pids


def get_python_processes():
    """Return list of dicts with pid, cmdline, creation_date for python.exe processes.

    Uses tasklist for PID enumeration and wmic for command line details.
    """
    pids = get_running_pids()
    if not pids:
        return []

    try:
        wmic_out = subprocess.run(
            ['wmic', 'process', 'where', "name='python.exe'",
             'get', 'ProcessId,CreationDate,CommandLine', '/FORMAT:CSV'],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return [{'pid': pid, 'cmdline': '', 'creation_date': ''} for pid in pids]

    processes = []
    for row in csv.reader(io.StringIO(wmic_out.stdout)):
        if len(row) < 4:
            continue
        pid_str = row[3].strip()
        if pid_str.isdigit() and int(pid_str) in pids:
            processes.append({
                'pid': int(pid_str),
                'cmdline': row[1].strip(),
                'creation_date': row[2].strip(),
            })
    return processes


def get_process_memory(pid):
    """Get memory string from tasklist CSV for a PID."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
        for row in csv.reader(io.StringIO(result.stdout)):
            if len(row) >= 5 and row[1].strip() == str(pid):
                return row[4].strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return 'N/A'


def try_get_cpu_time(pid):
    """Try to get CPU time string via wmic. Returns formatted string or None."""
    try:
        result = subprocess.run(
            ['wmic', 'process', 'where', f'processid={pid}',
             'get', 'KernelModeTime,UserModeTime', '/FORMAT:CSV'],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
        for row in csv.reader(io.StringIO(result.stdout)):
            if len(row) >= 3 and row[0].strip().upper() != 'NODE':
                kernel = int(row[0].strip())
                user = int(row[1].strip())
                total_sec = (kernel + user) / 10_000_000
                if total_sec < 60:
                    return f'CPU {total_sec:.1f}s'
                return f'CPU {int(total_sec // 60)}m{int(total_sec % 60)}s'
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError, IndexError):
        pass
    return None


def get_process_usage_str(pid):
    """Get combined CPU + memory string for a PID."""
    parts = []
    cpu = try_get_cpu_time(pid)
    if cpu:
        parts.append(cpu)
    mem = get_process_memory(pid)
    if mem != 'N/A':
        parts.append(f'Mem {mem}')
    return ', '.join(parts) if parts else 'N/A'


def parse_wmic_date(wmic_str):
    """Parse WMIC datetime YYYYMMDDHHMMSS.ffffff+ZZZ to datetime."""
    if not wmic_str or len(wmic_str) < 14:
        return None
    try:
        return datetime.strptime(wmic_str[:14], '%Y%m%d%H%M%S')
    except ValueError:
        return None


def process_check():
    """Check daily_articles.py processes. Returns (status_str, error_count, details_list)."""
    procs = get_python_processes()
    daily = [p for p in procs if 'daily_articles' in p['cmdline'].lower()]

    if daily:
        parts = []
        for p in daily:
            usage_str = get_process_usage_str(p['pid'])
            start = parse_wmic_date(p['creation_date'])
            start_s = start.strftime('%H:%M') if start else '??:??'
            started_t = start and start.date() == TODAY
            flag = 'today' if started_t else 'old session'
            parts.append(f'PID {p["pid"]}, started {start_s}, {flag}, {usage_str}')
        return f'RUNNING ({len(daily)} proc)', 0, parts

    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            last_run = state.get('last_run', '')
            if last_run == TODAY.isoformat():
                return 'COMPLETED', 0, [f'last run today ({last_run})']
        except (json.JSONDecodeError, OSError):
            pass

    last_run_str = ''
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            last_run_str = state.get('last_run', '')
        except (json.JSONDecodeError, OSError):
            pass

    expected_time = NOW.replace(hour=EXPECTED_RUN_HOUR, minute=0, second=0, microsecond=0)

    history = f'last run was {last_run_str}' if last_run_str else 'no prior run recorded'

    if NOW >= expected_time:
        return 'ERROR', 1, [f'not started (past {EXPECTED_RUN_HOUR}:00, {history})']

    return 'WAITING', 0, [f'before {EXPECTED_RUN_HOUR}:00, {history}']


def articles_check():
    """Scan all site dirs for articles generated today.

    Returns (ok_count, total_new, total_sites, zero_sites, error_count).
    """
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, 0, 0, [], 1

    sites = config.get('sites', [])
    ok_count = 0
    total_new = 0
    zero_sites = []

    for site in sites:
        site_dir = ROOT / site['dir']
        if not site_dir.is_dir():
            zero_sites.append(site['dir'])
            continue

        count_today = 0
        for pattern in ('article-*.html', 'blog-*.html'):
            for f in site_dir.glob(pattern):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime.date() == TODAY:
                    count_today += 1

        total_new += count_today
        if count_today >= 1:
            ok_count += 1
        else:
            zero_sites.append(site['dir'])

    err = 1 if total_new < EXPECTED_MIN_ARTICLES else 0
    return ok_count, total_new, len(sites), zero_sites, err


def zombie_check(cleanup):
    """Check for stale daily_articles PID. Returns (status_str, error_count, details_list)."""
    if not PID_FILE.exists():
        return 'CLEAN', 0, ['no PID file']

    pid_str = PID_FILE.read_text().strip()
    if not pid_str or not pid_str.isdigit():
        return 'CLEAN', 0, ['invalid PID file']

    pid = int(pid_str)
    procs = get_python_processes()
    match = [p for p in procs if p['pid'] == pid]

    if not match:
        return 'CLEAN', 0, [f'PID {pid} not running']

    p = match[0]
    start = parse_wmic_date(p['creation_date'])
    if start and start.date() >= TODAY:
        return 'CLEAN', 0, [f'PID {pid} running since today']

    usage_str = get_process_usage_str(pid)
    start_s = start.strftime('%Y-%m-%d %H:%M') if start else 'unknown'
    detail = f'ZOMBIE PID {pid} (started {start_s}, {usage_str})'

    if cleanup:
        try:
            kill = subprocess.run(
                ['taskkill', '/PID', str(pid), '/F'],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
            )
            if kill.returncode == 0:
                PID_FILE.write_text('')
                return 'KILLED', 0, [f'killed PID {pid}']
            return 'ZOMBIE', 1, [f'{detail} kill failed: {kill.stderr.strip()}']
        except (subprocess.TimeoutExpired, OSError) as e:
            return 'ZOMBIE', 1, [f'{detail} kill error: {e}']

    return 'ZOMBIE', 1, [detail]


def check_content_quality():
    """Randomly sample today's articles and verify content quality.

    Checks: image presence, blockquote presence, AI cliches, word count,
    title-content keyword match.

    Returns (status_str, error_count, details_list).
    """
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return 'ERROR', 1, ['cannot read site_config.json']

    sites = config.get('sites', [])

    # Find sites with articles modified today
    sites_with_articles = []
    articles_by_site = {}

    for site in sites:
        site_dir = ROOT / site['dir']
        if not site_dir.is_dir():
            continue

        today_articles = []
        for pattern in ('article-*.html', 'blog-*.html'):
            for f in site_dir.glob(pattern):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime.date() == TODAY:
                    today_articles.append(f)

        if today_articles:
            sites_with_articles.append(site['dir'])
            articles_by_site[site['dir']] = today_articles

    if not sites_with_articles:
        return 'SKIP', 0, ['no articles modified today']

    # Randomly pick up to 3 sites
    sample_count = min(3, len(sites_with_articles))
    picked_sites = random.sample(sites_with_articles, sample_count)

    cliches = [
        "In this guide, we'll",
        "Let's dive in",
        "Moreover",
        "In conclusion",
        "whether you're a",
        "delve into",
        "in today's fast-paced world",
    ]

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'not', 'no', 'nor', 'it',
        'its', 'this', 'that', 'these', 'those', 'from', 'as', 'at', 'about',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
        'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
        'up', 'down', 'onto', 'upon',
    }

    details = []
    passed = 0
    total_errors = 0

    for site_dir in picked_sites:
        articles = articles_by_site[site_dir]
        article_path = random.choice(articles)
        rel_path = f"{site_dir}/{article_path.name}"

        try:
            html = article_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            details.append(f"           {rel_path}: ERROR (unreadable)")
            total_errors += 1
            continue

        issues = []

        # a. Image check
        img_count = html.count('<img src=')
        if img_count < 1:
            issues.append('img=0')

        # b. Blockquote check
        blockquote_count = html.count('<blockquote')
        if blockquote_count < 1:
            issues.append('block=0')

        # c. AI cliché scan
        html_lower = html.lower()
        found_cliches = []
        for cliche in cliches:
            if cliche.lower() in html_lower:
                found_cliches.append(cliche)

        # d. Word count (extract body text, strip HTML tags)
        body_start = html.lower().find('<body')
        body_end = html.lower().rfind('</body>')
        if body_start >= 0 and body_end > body_start:
            body_content = html[body_start:body_end]
            text = re.sub(r'<[^>]+>', ' ', body_content)
            text = re.sub(r'\s+', ' ', text).strip()
            word_count = len(text.split())
        else:
            body_content = ''
            word_count = 0

        if word_count < 500:
            issues.append(f'words={word_count}')

        # e. Title-content match
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title_text = title_match.group(1).strip() if title_match else ''
        # Strip site name suffix (e.g. " - HealthyEats")
        for sep in (' - ', ' | ', ' — '):
            if sep in title_text:
                title_text = title_text.split(sep)[0]
                break

        title_keywords = [
            w.lower() for w in title_text.split()
            if w.lower() not in stop_words and len(w) > 2
        ]

        body_lower = body_content.lower() if body_content else html.lower()
        body_text = re.sub(r'<[^>]+>', ' ', body_lower)

        match_count = sum(1 for kw in title_keywords if kw in body_text)
        if match_count < 2:
            issues.append('title mismatch')

        # Build result line
        if issues:
            total_errors += 1
            parts = ['FAIL']
            parts.append(f'img={img_count}')
            if blockquote_count < 1:
                parts.append('block=0')
            else:
                parts.append(f'block={blockquote_count}')
            parts.append(f'words={word_count}')
            if found_cliches:
                cliche_str = ', '.join(f'"{c}"' for c in found_cliches)
                parts.append(f'{len(found_cliches)} cliches: {cliche_str}')
            else:
                parts.append('no cliche')
            if match_count < 2:
                parts.append('title mismatch')
            else:
                parts.append('title matches')
            details.append(f"           {rel_path}: {' '.join(parts)}")
        else:
            passed += 1
            details.append(
                f"           {rel_path}: PASS"
                f" (img={img_count}, block={blockquote_count},"
                f" words={word_count}, no cliche, title matches)"
            )

    status_str = f'{passed}/{len(picked_sites)} spot-checks passed'
    return status_str, total_errors, details


def main():
    quick = '--quick' in sys.argv
    cleanup = '--cleanup' in sys.argv
    quality_only = '--quality' in sys.argv
    total_errors = 0
    lines = []

    if quality_only:
        # --quality: run only the quality check
        lines.append(f'=== daily_articles Quality Spot-Check {NOW.strftime("%Y-%m-%d %H:%M")} ===')
        lines.append('')
        q_status, q_errors, q_details = check_content_quality()
        total_errors += q_errors
        lines.append(f'Quality:   {q_status}')
        lines.extend(q_details)
        lines.append('')
        if total_errors == 0:
            lines.append('Status:    ALL OK')
        else:
            lines.append(f'Status:    {total_errors} ISSUE(S)')
        for line in lines:
            print(line)
        return 1 if total_errors > 0 else 0

    if not quick:
        lines.append(f'=== daily_articles Health Check {NOW.strftime("%Y-%m-%d %H:%M")} ===')
        lines.append('')

    p_status, p_errors, p_details = process_check()
    total_errors += p_errors
    if not quick or p_errors:
        p_detail_str = ' | '.join(p_details) if p_details else ''
        lines.append(f'Process:   {p_status}{" (" + p_detail_str + ")" if p_detail_str else ""}')

    a_ok, a_new, a_total, a_zero, a_errors = articles_check()
    total_errors += a_errors
    if not quick or a_errors or a_zero:
        lines.append(
            f'Articles:  {a_ok}/{a_total} sites OK'
            f' ({a_new} new today, expected >= {EXPECTED_MIN_ARTICLES})'
        )
        if a_zero:
            lines.append(f'           Zero articles today: {", ".join(a_zero)}')

    z_status, z_errors, z_details = zombie_check(cleanup)
    total_errors += z_errors
    if not quick or z_errors:
        z_detail_str = ' | '.join(z_details) if z_details else ''
        lines.append(f'Zombies:   {z_status}{" (" + z_detail_str + ")" if z_detail_str else ""}')

    # Quality check (skipped in --quick mode, too slow)
    if not quick:
        q_status, q_errors, q_details = check_content_quality()
        total_errors += q_errors
        lines.append(f'Quality:   {q_status}')
        lines.extend(q_details)

    if not quick:
        lines.append('')
        if total_errors == 0:
            lines.append('Status:    ALL OK')
        else:
            lines.append(f'Status:    {total_errors} ISSUE(S)')

    for line in lines:
        print(line)

    return 1 if total_errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
