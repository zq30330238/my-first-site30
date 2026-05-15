# Edge TTS 男声朗读脚本
$speechFile = "C:\Users\Administrator\AppData\Local\Temp\claude-speech.txt"
$outputMp3 = "C:\Users\Administrator\AppData\Local\Temp\claude-speech.mp3"
$python = "C:\Program Files\Python312\python.exe"

if (-not (Test-Path $speechFile)) { exit }

$text = Get-Content $speechFile -Raw -Encoding UTF8

# 简单清理 Markdown 符号
$text = $text -replace "```[^`]*```", ""
$text = $text -replace "`*`*", ""
$text = $text -replace "`*", ""
$text = $text -replace "#", ""
$text = $text -replace "`[", ""
$text = $text -replace "`]", ""
$text = $text -replace "`(", ""
$text = $text -replace "`)", ""

$voice = "zh-CN-YunyangNeural"

# 把文本写到一个临时文件，防止命令行传参出错
$textFile = "C:\Users\Administrator\AppData\Local\Temp\claude-tts-input.txt"
$text | Out-File -FilePath $textFile -Encoding UTF8 -NoNewline

# 用 edge-tts 的 -f 参数从文件读
& $python -m edge_tts --voice $voice -f $textFile --write-media $outputMp3

# 播放
if (Test-Path $outputMp3) {
    Start-Process $outputMp3 -WindowStyle Minimized
    Start-Sleep -Milliseconds 800
}
