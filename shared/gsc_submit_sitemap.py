"""Auto-submit sitemaps to Google Search Console via API.
One-time OAuth auth, then fully automated.

Setup:
1. Go to https://console.cloud.google.com
2. Create project "jycsd-sites" or use existing
3. Enable "Google Search Console API"
4. Go to APIs & Services > Credentials
5. Create OAuth 2.0 Client ID > Desktop App
6. Download JSON, save as d:/AI网站文件夹/backup-config/gsc-credentials.json
7. Run: python shared/gsc_submit_sitemap.py --auth (first time only)
8. After auth, run without --auth to submit all sitemaps
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
CREDS_FILE = ROOT / 'backup-config' / 'gsc-credentials.json'
TOKEN_FILE = ROOT / 'backup-config' / 'gsc-token.json'

SITES = {
    'healthy-jycsd': 'https://healthy.jycsd.com',
    'pets-jycsd': 'https://pets.jycsd.com',
    'home-jycsd': 'https://home.jycsd.com',
    'finance-jycsd': 'https://finance.jycsd.com',
    'tech-jycsd': 'https://tech.jycsd.com',
    'travel-jycsd': 'https://travel.jycsd.com',
    'main-site': 'https://www.jycsd.com',
}

SCOPES = ['https://www.googleapis.com/auth/webmasters']


def get_credentials():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def submit_sitemap(creds, site_url, sitemap_name='sitemap.xml'):
    from googleapiclient.discovery import build
    service = build('searchconsole', 'v1', credentials=creds)
    site_url = site_url.rstrip('/') + '/'

    try:
        service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_name).execute()
        print(f'  OK: {site_url}{sitemap_name}')
        return True
    except Exception as e:
        print(f'  FAIL {site_url}: {e}')
        return False


def main():
    if '--auth' in sys.argv:
        print('Starting OAuth flow...')
        print('A browser window will open. Log in with the Google account that owns Search Console.')
        creds = get_credentials()
        print(f'Token saved to {TOKEN_FILE}')
        print('Auth complete! Now run without --auth to submit sitemaps.')
        return

    if not CREDS_FILE.exists():
        print(f'ERROR: Credentials file not found at {CREDS_FILE}')
        print('1. Go to https://console.cloud.google.com/apis/credentials')
        print('2. Create OAuth 2.0 Client ID > Desktop App')
        print(f'3. Download JSON and save as {CREDS_FILE}')
        print('4. Run: python shared/gsc_submit_sitemap.py --auth')
        return 1

    print('Authenticating...')
    creds = get_credentials()

    success = 0
    failed = []
    for name, url in SITES.items():
        print(f'{name}: {url}')
        if submit_sitemap(creds, url):
            success += 1
        else:
            failed.append(name)

    print(f'\n{success}/{len(SITES)} submitted successfully')
    if failed:
        print(f'Failed: {failed}')


if __name__ == '__main__':
    sys.exit(main() or 0)
