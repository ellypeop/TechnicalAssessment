Param(
	[string]$Query = "What services does Samsic UK provide and what are key considerations in bid management for UK FM providers?",
	[int]$MaxResults = 8,
	[int]$LocalMaxChunks = 0,
	[string]$Out = "report_samsic_web.md"
)

Write-Host "== Research Agent: Web Lookup Test (Samsic UK) =="

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

# Run agent with web-only (exclude default Samsic DOCX)
Write-Host "Running research for query: $Query"
python -m research_agent.cli --no-include-samsic --max-results $MaxResults --local-max-chunks $LocalMaxChunks --out $Out "$Query"

if ($LASTEXITCODE -ne 0) {
	Write-Error "Research agent exited with code $LASTEXITCODE"
	exit $LASTEXITCODE
}

Write-Host "Saved report to $Out"
