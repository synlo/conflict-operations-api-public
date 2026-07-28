[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path,
    [string]$DestinationRoot,
    [string]$ReceiptPath
)

$ErrorActionPreference = "Stop"
$source = [System.IO.Path]::GetFullPath($SourceRoot).TrimEnd("\")
if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "SourceRoot is not a directory."
}

if ([string]::IsNullOrWhiteSpace($DestinationRoot)) {
    $DestinationRoot = Join-Path ([System.IO.Path]::GetTempPath()) (
        "coapi-public-export-" + [guid]::NewGuid().ToString("N")
    )
}
$destination = [System.IO.Path]::GetFullPath($DestinationRoot).TrimEnd("\")
if ($destination.StartsWith($source + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "DestinationRoot must be outside SourceRoot."
}
if (Test-Path -LiteralPath $destination) {
    $existing = @(Get-ChildItem -LiteralPath $destination -Force -ErrorAction Stop)
    if ($existing.Count -gt 0) {
        throw "DestinationRoot must be new or empty."
    }
}

$audit = Join-Path $source "Tools\COAPI\Public\audit_public_export.py"
$arguments = @(
    "-3", $audit, "export",
    "--source-root", $source,
    "--destination-root", $destination,
    "--allowlist", (Join-Path $source ".publicmirror\public-source-allowlist.txt"),
    "--denylist", (Join-Path $source ".publicmirror\public-path-denylist.txt"),
    "--patterns", (Join-Path $source ".publicmirror\public-content-deny-patterns.json"),
    "--provenance", (Join-Path $source ".publicmirror\public-provenance.json"),
    "--placeholders", (Join-Path $source ".publicmirror\public-placeholders.json")
)
if (-not [string]::IsNullOrWhiteSpace($ReceiptPath)) {
    $arguments += @("--output", [System.IO.Path]::GetFullPath($ReceiptPath))
}

& py @arguments
exit $LASTEXITCODE
