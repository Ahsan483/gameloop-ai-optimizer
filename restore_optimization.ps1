param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"
$manifestPath = Join-Path $BackupPath "manifest.json"
if (-not (Test-Path $manifestPath)) { throw "Backup manifest not found: $manifestPath" }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$base = "C:\Program Files\TxGameAssistant"
foreach ($relative in $manifest.files) {
    $source = Join-Path $BackupPath $relative
    $target = Join-Path $base $relative
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
}
$gameModePath = Join-Path $BackupPath "windows_gamemode.json"
if (Test-Path -LiteralPath $gameModePath) {
    $gameMode = Get-Content $gameModePath -Raw | ConvertFrom-Json
    $key = "HKCU:\Software\Microsoft\GameBar"
    if ($null -eq $gameMode.AllowAutoGameMode) {
        Remove-ItemProperty -Path $key -Name AllowAutoGameMode -ErrorAction SilentlyContinue
    } else {
        Set-ItemProperty -Path $key -Name AllowAutoGameMode -Type DWord -Value ([int]$gameMode.AllowAutoGameMode)
    }
    if ($null -eq $gameMode.AutoGameModeEnabled) {
        Remove-ItemProperty -Path $key -Name AutoGameModeEnabled -ErrorAction SilentlyContinue
    } else {
        Set-ItemProperty -Path $key -Name AutoGameModeEnabled -Type DWord -Value ([int]$gameMode.AutoGameModeEnabled)
    }
}
Write-Output "Restored configuration files from $BackupPath"