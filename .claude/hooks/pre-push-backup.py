"""Pre-push hook — auto-backup user configs before each push"""
import subprocess, sys
subprocess.run([sys.executable, r"d:\AI网站文件夹\shared\backup-config.py"], check=False)
print('{"continue": true}')
