[CmdletBinding()]
param(
    [ValidateSet("Acquire", "Release", "Status")]
    [string]$Action = "Status",
    [ValidateSet("repository", "workbench", "release")]
    [string]$Domain = "repository",
    [string]$TaskId = "",
    [ValidateSet("RECOVERY", "DEVELOPMENT", "RELEASE")]
    [string]$Mode = "DEVELOPMENT",
    [int]$OwnerPid = $PID,
    [string]$Nonce = ""
)

$ErrorActionPreference = "Stop"
$core = Join-Path $PSScriptRoot "coapi_control.py"
$arguments = @("-3", $core, "lock", $Action.ToLowerInvariant())

if ($Action -eq "Acquire") {
    if ([string]::IsNullOrWhiteSpace($TaskId)) {
        throw "TaskId is required when acquiring a lock"
    }
    $arguments += @("--domain", $Domain, "--task-id", $TaskId, "--mode", $Mode, "--owner-pid", "$OwnerPid")
}
elseif ($Action -eq "Release") {
    $arguments += @("--domain", $Domain, "--owner-pid", "$OwnerPid")
    if (-not [string]::IsNullOrWhiteSpace($Nonce)) {
        $arguments += @("--nonce", $Nonce)
    }
}

& py @arguments
exit $LASTEXITCODE
