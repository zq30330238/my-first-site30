"""Robots.txt and ads.txt compliance check for all sites"""
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

REQUIRED_ROBOTS = ['User-agent:', 'Allow:', 'Sitemap:']
REQUIRED_ADS = ['google.com', 'pub-']

def check_robots(path):
    if not path.exists():
        return ['Missing robots.txt']
    content = path.read_text(encoding='utf-8')
    issues = []
    for r in REQUIRED_ROBOTS:
        if r not in content:
            issues.append(f'robots.txt missing "{r}"')
    return issues

def check_ads(path):
    if not path.exists():
        return ['Missing ads.txt']
    content = path.read_text(encoding='utf-8')
    issues = []
    for r in REQUIRED_ADS:
        if r not in content:
            issues.append(f'ads.txt missing "{r}"')
    return issues

def main():
    all_ok = True
    for d in DIRS:
        dir_path = ROOT / d
        robot_issues = check_robots(dir_path / 'robots.txt')
        ads_issues = check_ads(dir_path / 'ads.txt')

        status = 'OK' if not robot_issues and not ads_issues else 'ISSUES'
        if status != 'OK':
            all_ok = False
        print(f'{d}: robots.txt={robot_issues or "OK"}, ads.txt={ads_issues or "OK"}')

    if all_ok:
        print('\nAll sites have valid robots.txt and ads.txt.')

if __name__ == '__main__':
    main()
