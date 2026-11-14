<#
.SYNOPSIS
  Copy a project folder from Windows to the Raspberry Pi and optionally run it.
  Uses the OpenSSH client and tar that ship with Windows 10/11.

.EXAMPLE
  .\deploy.ps1 .\myapp
  .\deploy.ps1 .\myapp -Run "python3 main.py"
  .\deploy.ps1 .\myapp -PiHost pi@192.168.1.50 -Run "python3 main.py"
#>
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$PiHost = $(if ($env:PI_HOST) { $env:PI_HOST } else { "pi@raspberrypi.local" }),
    [string]$Dest,
    [string]$Run
)

$ErrorActionPreference = "Stop"
$src = (Resolve-Path $Source).Path
$name = Split-Path $src -Leaf
if (-not $Dest) { $Dest = "~/$name" }

$archive = Join-Path $env:TEMP "handlet-deploy-$name.tgz"
Write-Host "==> Packing $src"
tar -C $src -czf $archive --exclude=.git --exclude=__pycache__ --exclude=.venv --exclude=node_modules .
if ($LASTEXITCODE -ne 0) { throw "tar failed" }

Write-Host "==> Uploading to ${PiHost}:$Dest"
scp -q $archive "${PiHost}:/tmp/handlet-deploy.tgz"
if ($LASTEXITCODE -ne 0) { throw "scp failed" }
ssh $PiHost "mkdir -p $Dest && tar -xzf /tmp/handlet-deploy.tgz -C $Dest && rm /tmp/handlet-deploy.tgz"
Remove-Item $archive

if ($Run) {
    Write-Host "==> Running: $Run"
    ssh -t $PiHost "cd $Dest && $Run"
}
