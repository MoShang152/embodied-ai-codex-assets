param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $repoRoot "skills"

if ($env:CODEX_HOME) {
    $codexHome = $env:CODEX_HOME
} else {
    $codexHome = Join-Path $HOME ".codex"
}

$destRoot = Join-Path $codexHome "skills"
New-Item -ItemType Directory -Force -Path $destRoot | Out-Null

Get-ChildItem -Directory $sourceRoot | ForEach-Object {
    $dest = Join-Path $destRoot $_.Name
    if ((Test-Path $dest) -and (-not $Force)) {
        throw "Skill already exists: $dest. Re-run with -Force to overwrite."
    }
    if (Test-Path $dest) {
        Remove-Item -Recurse -Force -LiteralPath $dest
    }
    Copy-Item -Recurse -LiteralPath $_.FullName -Destination $dest
    Write-Output "Installed $($_.Name) -> $dest"
}

Write-Output "Done. Restart Codex or start a new session if newly installed skills are not visible."
