[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory)][string]$TaskId,
    [Parameter(Mandatory)][string]$Phase,
    [Parameter(Mandatory)][string]$HypothesisId,
    [Parameter(Mandatory)][string]$OperationKind,
    [Parameter(Mandatory)][ValidateRange(1, 3600)][int]$TimeoutSeconds,
    [Parameter(Mandatory)][string]$ExpectedTransition,
    [string]$WorkingDirectory = (Get-Location).Path,
    [string[]]$InputHash = @(),
    [string[]]$ExpectedArtifact = @(),
    [int]$LockOwnerPid = 0,
    [Parameter(Mandatory, ValueFromRemainingArguments)][string[]]$Command
)

$ErrorActionPreference = "Stop"
$core = Join-Path $PSScriptRoot "coapi_control.py"
$arguments = @(
    "-3", $core, "bounded",
    "--task-id", $TaskId,
    "--phase", $Phase,
    "--hypothesis-id", $HypothesisId,
    "--operation-kind", $OperationKind,
    "--timeout-seconds", "$TimeoutSeconds",
    "--expected-transition", $ExpectedTransition,
    "--cwd", $WorkingDirectory
)
foreach ($value in $InputHash) {
    $arguments += @("--input-hash", $value)
}
foreach ($value in $ExpectedArtifact) {
    $arguments += @("--expected-artifact", $value)
}
if ($LockOwnerPid -gt 0) {
    $arguments += @("--lock-owner-pid", "$LockOwnerPid")
}
$arguments += "--"
$arguments += $Command

& py @arguments
exit $LASTEXITCODE
