"""
一次性 OAuth 授权工具 —— 获取 Google AdSense API Refresh Token
运行后打开浏览器，登录 Google 授权，返回 refresh_token。
手动运行，不在管线中。

前置条件:
  export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
  export GOOGLE_CLIENT_SECRET="GOCSPX-xxxx"

运行: py shared/ad_auth.py
成功后打印 refresh_token，将其设为环境变量 GOOGLE_REFRESH_TOKEN。
"""
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/adsense.readonly"]

def main():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("错误: 请先设置环境变量 GOOGLE_CLIENT_ID 和 GOOGLE_CLIENT_SECRET")
        print()
        print("1. 前往 https://console.cloud.google.com/apis/credentials")
        print("2. 创建 OAuth 2.0 Client ID（桌面应用类型）")
        print("3. 设置环境变量:")
        print('   export GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"')
        print('   export GOOGLE_CLIENT_SECRET="GOCSPX-xxx"')
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("缺少依赖: pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print()
    print("=" * 50)
    print("授权成功！")
    print()
    print("Refresh Token (请保存到环境变量):")
    print(f"  {creds.refresh_token}")
    print()
    print("设置方法:")
    print(f'  export GOOGLE_REFRESH_TOKEN="{creds.refresh_token}"')
    print("=" * 50)
    print()
    print("此后 ad_monitor.py 可自动使用该 token 获取收益数据。")

if __name__ == "__main__":
    main()
