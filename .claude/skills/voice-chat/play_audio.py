"""后台无声播放 Edge TTS 生成的 MP3（不弹任何窗口）"""
import subprocess, os, sys, time, tempfile

TTS_MP3 = os.path.join(tempfile.gettempdir(), "claude-voice-chat.mp3")
PYTHON = r"C:\Program Files\Python312\python.exe"

def play_mp3(filepath):
    """用 Windows MCI API 后台播放 MP3"""
    import ctypes
    import ctypes.wintypes

    buf = ctypes.create_unicode_buffer(260)

    # 关闭之前的播放
    ctypes.windll.winmm.mciSendStringW("close mp3", None, 0, None)

    # 打开 MP3 文件
    cmd = f'open "{filepath}" type mpegvideo alias mp3'
    ret = ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None)
    if ret != 0:
        ctypes.windll.winmm.mciGetErrorStringW(ret, buf, 260)
        return False

    # 播放
    ctypes.windll.winmm.mciSendStringW("play mp3", None, 0, None)
    return True

def generate_tts(text):
    """用 Edge TTS 生成男声 MP3"""
    text = text.replace("\n", " ").strip()
    if not text:
        return None

    input_file = os.path.join(tempfile.gettempdir(), "claude-tts-chat.txt")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(text)

    # 删除旧文件
    if os.path.exists(TTS_MP3):
        os.remove(TTS_MP3)

    subprocess.run([
        PYTHON, "-m", "edge_tts",
        "--voice", "zh-CN-YunyangNeural",
        "-f", input_file,
        "--write-media", TTS_MP3
    ], capture_output=True, timeout=30)

    if os.path.exists(TTS_MP3):
        return TTS_MP3
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: play_audio.py <text>")
        sys.exit(1)

    text = sys.argv[1]
    mp3 = generate_tts(text)
    if mp3:
        play_mp3(mp3)
        print("Playing...")
    else:
        print("TTS generation failed")
