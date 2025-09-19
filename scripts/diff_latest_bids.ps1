Param(
	[int]$Count = 2
)

$dir = "reports"
if (-not (Test-Path $dir)) {
	Write-Error "Reports directory not found: $dir"
	exit 1
}

$files = Get-ChildItem $dir -Filter "bid_*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First $Count
if ($files.Count -lt 2) {
	Write-Error "Need at least two versioned reports to diff."
	exit 1
}

$left = $files[1].FullName
$right = $files[0].FullName
Write-Host "Diffing:`nLEFT:  $left`nRIGHT: $right"

# Use built-in fc for a simple diff
fc "$left" "$right" | Out-Host
