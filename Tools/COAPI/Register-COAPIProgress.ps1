[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet(
        "INPUT_HASH_CHANGED",
        "UNIQUE_EVIDENCE_FOUND",
        "OWNER_IDENTIFIED",
        "TEST_STATE_CHANGED",
        "INTENDED_PATCH_WRITTEN",
        "STATE_TRANSITION"
    )]
    [string]$ProgressType,
    [Parameter(Mandatory)][string]$Phase,
    [string]$HypothesisId = "",
    [Parameter(Mandatory)][string]$Summary
)

$ErrorActionPreference = "Stop"
$core = Join-Path $PSScriptRoot "coapi_control.py"
$arguments = @(
    "-3", $core, "progress",
    "--progress-type", $ProgressType,
    "--phase", $Phase,
    "--summary", $Summary
)
if (-not [string]::IsNullOrWhiteSpace($HypothesisId)) {
    $arguments += @("--hypothesis-id", $HypothesisId)
}

& py @arguments
exit $LASTEXITCODE
