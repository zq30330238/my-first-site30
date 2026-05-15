mp3 = "C:\Users\Administrator\AppData\Local\Temp\claude-speech.mp3"

Set o = CreateObject("WScript.Shell")
o.Run "powershell -Command (New-Object Media.SoundPlayer '" & mp3 & "').PlaySync()", 0
