"""OAuth tool — get Google AdSense API Refresh Token
Usage: python -u shared/ad_auth.py
Prerequisites:
  set GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
  set GOOGLE_CLIENT_SECRET=GOCSPX-xxxx
"""
import os, sys

SCOPES = ["https://www.googleapis.com/auth/adsense.readonly"]
RESULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "refresh_token.txt")

def main():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Missing deps: pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = "http://localhost:8080"

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    print()
    print("=" * 60)
    print("A local server will start on http://localhost:8080")
    print("Copy the URL below and open it in Chrome")
    print("After authorizing, Google redirects back to localhost.")
    print("=" * 60)
    print(flush=True)

    creds = flow.run_local_server(
        host="localhost",
        port=8080,
        open_browser=False,
    )

    if creds.refresh_token:
        with open(RESULT_FILE, "w") as f:
            f.write(creds.refresh_token)

        print()
        print("=" * 50)
        print("SUCCESS!")
        print()
        print("Refresh Token:")
        print(f"  {creds.refresh_token}")
        print()
        print(f"Saved to {RESULT_FILE}")
        print("=" * 50)

if __name__ == "__main__":
    main()
