"""抖音视频内容解析 - 支持元数据提取和语音转文字"""
import re, json, os, sys, requests, subprocess, tempfile

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1"
}
FFMPEG = r"C:\Users\Administrator\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffmpeg.exe"
VOSK_SERVER = "http://127.0.0.1:9877/transcribe"


def parse_douyin(share_url):
    """从抖音分享链接提取视频信息"""
    resp = requests.get(share_url, headers=HEADERS, allow_redirects=True, timeout=15)
    final_url = resp.url
    video_id = final_url.split("?")[0].strip("/").split("/")[-1]

    api_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    resp2 = requests.get(api_url, headers=HEADERS, timeout=15)
    html = resp2.text

    pattern = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", re.DOTALL)
    match = pattern.search(html)
    if not match:
        return {"status": "error", "error": "无法解析视频信息"}

    data = json.loads(match.group(1).strip())

    VIDEO_ID_KEY = "video_(id)/page"
    NOTE_ID_KEY = "note_(id)/page"
    loader = data.get("loaderData", {})

    if VIDEO_ID_KEY in loader:
        video_info = loader[VIDEO_ID_KEY]["videoInfoRes"]
    elif NOTE_ID_KEY in loader:
        video_info = loader[NOTE_ID_KEY]["videoInfoRes"]
    else:
        return {"status": "error", "error": "无法找到视频数据"}

    item = video_info["item_list"][0]
    video_url = item["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
    desc = item.get("desc", "").strip() or f"douyin_{video_id}"
    author = item.get("author", {})
    stats = item.get("stats", {})

    return {
        "status": "success",
        "video_id": video_id,
        "title": desc,
        "author": author.get("nickname", ""),
        "likes": stats.get("digg_count", 0),
        "comments": stats.get("comment_count", 0),
        "shares": stats.get("share_count", 0),
        "download_url": video_url
    }


def transcribe_video(share_url):
    """完整流程：解析 → 流式下载+提取音频 → 语音转文字（通过Vosk常驻服务）"""
    info = parse_douyin(share_url)
    if info["status"] != "success":
        return info

    print(f"视频: {info['title'][:50]}...", file=sys.stderr)
    print(f"作者: {info['author']}", file=sys.stderr)

    try:
        # 流式下载视频 → 管道给ffmpeg提取音频 → 直接得到WAV数据
        print("下载+提取音频中...", file=sys.stderr)
        download_resp = requests.get(info["download_url"], headers=HEADERS, timeout=120, stream=True)
        size_mb = int(download_resp.headers.get("content-length", 0)) / 1024 / 1024
        print(f"视频大小: {size_mb:.1f}MB", file=sys.stderr)

        ffmpeg_cmd = [
            FFMPEG, "-i", "pipe:0", "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", "-f", "wav", "pipe:1", "-y"
        ]
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        # 流式写入ffmpeg stdin（边下载边处理）
        def feed_ffmpeg():
            for chunk in download_resp.iter_content(chunk_size=65536):
                if chunk:
                    proc.stdin.write(chunk)
            proc.stdin.close()

        import threading
        feeder = threading.Thread(target=feed_ffmpeg)
        feeder.start()

        # 读取ffmpeg输出的WAV数据
        audio_data = proc.stdout.read()
        feeder.join()

        # 语音转文字（通过Vosk常驻服务）
        print(f"语音识别中... (音频 {len(audio_data)/1000:.0f}KB)", file=sys.stderr)
        resp = requests.post(VOSK_SERVER, data=audio_data, timeout=600)
        if resp.status_code == 200:
            text = resp.json().get("text", "").strip()
            info["transcript"] = text
            print(f"识别结果: {text}", file=sys.stderr)
        else:
            info["transcript"] = ""
            info["transcript_error"] = f"Vosk server error: {resp.status_code}"

    except Exception as e:
        info["transcript"] = ""
        info["transcript_error"] = str(e)

    return info


if __name__ == "__main__":
    import sys
    url = None
    mode = "info"  # info | transcribe

    args = sys.argv[1:]
    if "--transcribe" in args:
        mode = "transcribe"
        args.remove("--transcribe")
    if args:
        url = args[0]

    if not url:
        print(json.dumps({"status": "error", "error": "请提供抖音分享链接"}, ensure_ascii=False))
        sys.exit(1)

    try:
        if mode == "transcribe":
            result = transcribe_video(url)
        else:
            result = parse_douyin(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
