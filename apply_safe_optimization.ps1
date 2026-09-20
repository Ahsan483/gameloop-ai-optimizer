param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"
$manifest = Join-Path $BackupPath "manifest.json"
if (-not (Test-Path -LiteralPath $manifest)) {
    throw "Refusing to change settings because the backup manifest was not found: $manifest"
}

$key = "HKCU:\Software\Microsoft\GameBar"
$before = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
$oldAllow = if ($null -ne $before) { $before.AllowAutoGameMode } else { $null }
$oldEnabled = if ($null -ne $before) { $before.AutoGameModeEnabled } else { $null }

New-Item -Path $key -Force | Out-Null
Set-ItemProperty -Path $key -Name AllowAutoGameMode -Type DWord -Value 1
Set-ItemProperty -Path $key -Name AutoGameModeEnabled -Type DWord -Value 1

$logPath = Join-Path $PSScriptRoot "optimization_log.json"
$log = if (Test-Path $logPath) { Get-Content $logPath -Raw | ConvertFrom-Json } else { [pscustomobject]@{ changes = @() } }
$entry = [pscustomobject]@{
    experiment_id = "game-mode-001"
    timestamp = (Get-Date).ToString("o")
    setting_changed = "HKCU:\Software\Microsoft\GameBar"
    old_value = "AllowAutoGameMode=$oldAllow; AutoGameModeEnabled=$oldEnabled"
    new_value = "AllowAutoGameMode=1; AutoGameModeEnabled=1"
    reason = "Enable Windows Game Mode scheduling support; Ultimate Performance is already active."
    risk = "Low"
    reversible = $true
    expected_effect = "Possible reduction in background scheduling interference; FPS improvement is not guaranteed."
}
$changes = @($log.changes) + $entry
[pscustomobject]@{
    created_at = $log.created_at
    changes = $changes
    note = "Only explicitly logged, reversible changes are permitted."
} | ConvertTo-Json -Depth 6 | Set-Content -Path $logPath -Encoding UTF8

Write-Output "Enabled Windows Game Mode registry settings. Restart GameLoop before measuring."