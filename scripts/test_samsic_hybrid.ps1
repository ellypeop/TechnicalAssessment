Param(
	[string]$Query = "From Samsic UK's context, what are key bid management requirements and how do they align with current UK FM market expectations?",
	[int]$MaxResults = 8,
	[int]$LocalMaxChunks = 3,
	[string]$Out = "report_samsic_hybrid.md",
	[string[]]$Docs = @()
)

Write-Host "== Research Agent: Hybrid Test (Local DOCX + Web) =="

# Ensure Python is available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
	Write-Error "Python is required but not found in PATH."
	exit 1
}

# Create venv if needed
if (-not (Test-Path ".venv")) {
	Write-Host "Creating virtual environment..."
	python -m venv .venv
}

# Activate venv
$venvActivate = ".venv/Scripts/Activate.ps1"
if (-not (Test-Path $venvActivate)) {
	Write-Error "Failed to find venv activation script at $venvActivate"
	exit 1
}
. $venvActivate

# Install deps
Write-Host "Installing dependencies..."
pip install -r requirements.txt | Out-Null

# Ensure .env exists
if (-not (Test-Path ".env")) {
	Write-Warning ".env not found. Create a .env with OPENAI_API_KEY before running."
}

# Build docs args (include default Samsic RFP if present)
$includeArgs = @()
$samsic = "data/raw/RFP - Bid Management Systems - Samsic UK.docx"
if (Test-Path $samsic) {
	$includeArgs += @('--include-samsic')
} else {
	$includeArgs += @('--no-include-samsic')
}
foreach ($d in $Docs) {
	$includeArgs += @('--doc', $d)
}

# Run agent with hybrid setup
Write-Host "Running research for query: $Query"
python -m research_agent.cli @includeArgs --max-results $MaxResults --local-max-chunks $LocalMaxChunks --out $Out "$Query"

if ($LASTEXITCODE -ne 0) {
	Write-Error "Research agent exited with code $LASTEXITCODE"
	exit $LASTEXITCODE
}

Write-Host "Saved report to $Out"
