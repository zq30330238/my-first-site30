"""Edge TTS 男声朗读 - 支持浏览器和原生两种播放模式"""
import subprocess, os, sys

speech_file = r"C:\Users\Administrator\AppData\Local\Temp\claude-speech.txt"
output_mp3 = r"C:\Users\Administrator\AppData\Local\Temp\claude-speech.mp3"
python_exe = r"C:\Program Files\Python312\python.exe"
player_html = r"d:\AI网站文件夹\.claude\skills\voice-reply\player.html"
play_vbs = r"d:\AI网站文件夹\.claude\skills\voice-reply\play.vbs"

PLAY_MODE = "browser"  # "browser" 弹窗播放(已验可用) / "native" 后台原生播放(待修)

if not os.path.exists(speech_file):
    sys.exit(0)

with open(speech_file, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("**", "").replace("`", "").replace("#", "")
text = text.replace("[", "").replace("]", "").replace("(", "").replace(")", "")

input_file = r"C:\Users\Administrator\AppData\Local\Temp\claude-tts-input.txt"
with open(input_file, "w", encoding="utf-8") as f:
    f.write(text)

subprocess.run([
    python_exe, "-m", "edge_tts",
    "--voice", "zh-CN-YunyangNeural",
    "-f", input_file,
    "--write-media", output_mp3
], capture_output=True)

if os.path.exists(output_mp3):
    if PLAY_MODE == "browser":
        os.startfile(player_html)
    else:
        # 原生后台播放，不弹任何窗口
        subprocess.Popen(["wscript", play_vbs])
