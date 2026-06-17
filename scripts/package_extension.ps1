$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$extension = Join-Path $root "extension"
$dist = Join-Path $root "dist"
$zip = Join-Path $dist "eureka-extension.zip"

if (Test-Path $dist) {
  Remove-Item -LiteralPath $dist -Recurse -Force
}
New-Item -ItemType Directory -Path $dist | Out-Null

Compress-Archive -Path (Join-Path $extension "*") -DestinationPath $zip -Force
Get-Item $zip | Select-Object FullName, Length
