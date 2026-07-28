[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path,
    [string]$ExportRoot
)

$ErrorActionPreference = "Stop"
$source = [System.IO.Path]::GetFullPath($SourceRoot).TrimEnd("\")
$audit = Join-Path $source "Tools\COAPI\Public\audit_public_export.py"
$patterns = Join-Path $source ".publicmirror\public-content-deny-patterns.json"

Push-Location $source
try {
    & py -3 -m unittest Tests.policy.test_stage1_control_plane Tools.COAPI.Public.test_audit_public_export
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if (-not [string]::IsNullOrWhiteSpace($ExportRoot)) {
        & py -3 $audit audit --root ([System.IO.Path]::GetFullPath($ExportRoot)) --patterns $patterns --denylist (Join-Path $source ".publicmirror\public-path-denylist.txt")
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & py -3 $audit verify --root ([System.IO.Path]::GetFullPath($ExportRoot))
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
} finally {
    Pop-Location
}

exit 0
