# Auto-rotate VSCode Claude Code session window
# Closes current window, opens a fresh one
# Handover memory is auto-written by Stop hook, auto-loaded by SessionStart hook

$projectDir = "d:\AI网站文件夹"

# Get current VSCode window PID (the one running this project)
$currentPid = $PID

# Find VSCode windows
$codeWindows = Get-Process -Name "Code" -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle

if (-not $codeWindows) {
    Write-Host "No VSCode windows found"
    exit 1
}

# Close current VSCode window first (graceful, then force)
$vsCodeProcs = Get-Process -Name "Code" -ErrorAction SilentlyContinue
foreach ($proc in $vsCodeProcs) {
    # Close the window — Claude's Stop hook fires and writes handover
    $proc.CloseMainWindow() | Out-Null
}

Start-Sleep -Seconds 3

# Force kill any remaining Code processes that didn't close gracefully
$remaining = Get-Process -Name "Code" -ErrorAction SilentlyContinue
foreach ($proc in $remaining) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

# Open new VSCode window with the project
Start-Process -FilePath "code" -ArgumentList "-n `"$projectDir`""

Write-Host "Window rotation complete — new session started"
