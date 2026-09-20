param(
    [string]$BackupRoot = (Join-Path $PSScriptRoot "backups")
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$destination = Join-Path $BackupRoot $timestamp
New-Item -ItemType Directory -Path $destination -Force | Out-Null

$files = @(
    "C:\Program Files\TxGameAssistant\ui\Config.ini",
    "C:\Program Files\TxGameAssistant\ui\ConfigPath.xml",
    "C:\Program Files\TxGameAssistant\ui\ConfigFile\AowConfig.ini",
    "C:\Program Files\TxGameAssistant\ui\ConfigFile\opengl.conf",
    "C:\Program Files\TxGameAssistant\ui\HardwareDetect.xml",
    "C:\Program Files\TxGameAssistant\ui\AowGame.xml"
)

$manifest = [ordered]@{
    created_at = (Get-Date).ToString("o")
    active_power_scheme = (powercfg /getactivescheme | Out-String).Trim()
    files = @()
}

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { continue }
    $relative = $file -replace '^C:\\Program Files\\TxGameAssistant\\', ''
    $target = Join-Path $destination (Split-Path $relative -Parent)
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -LiteralPath $file -Destination (Join-Path $destination $relative)
    $manifest.files += $relative
}

Get-ItemProperty "HKCU:\Software\Microsoft\GameBar" -ErrorAction SilentlyContinue |
    Select-Object AllowAutoGameMode,AutoGameModeEnabled |
    ConvertTo-Json | Set-Content (Join-Path $destination "windows_gamemode.json")
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -ErrorAction SilentlyContinue |
    Select-Object HwSchMode |
    ConvertTo-Json | Set-Content (Join-Path $destination "windows_hags.json")
$manifest | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $destination "manifest.json")
Write-Output $destination