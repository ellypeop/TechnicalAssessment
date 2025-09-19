## Research Agent (tender.io Bid Assistant)

A bid-writing assistant for tender.io. It parses an RFP document (DOCX), performs targeted web research, and produces a concise Markdown bid draft with explanations and inline citations to web sources. Keys are loaded from `.env`.

### Setup

1. Create and activate a virtual environment
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Ensure your `.env` at the project root contains:
```
OPENAI_API_KEY=...
SERPAPI_API_KEY=...      # optional, enables Google via SerpAPI
```

### Usage (Bid mode)

The agent uses the RFP file solely to extract the questions/criteria. Answers and citations are derived from web sources only.

You can either provide the RFP path explicitly or use the special phrase.

Examples:
```bash
# Using the special phrase (defaults to the Samsic RFP path if not provided)
python -m research_agent.cli "Write a bid for the RFP stored in file" --out bid.md

# Explicit RFP path
python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --max-results 8 --out bid_samsic.md
```

Options:
- `--max-results INT`: number of web search results to consider (default 8)
- `--out PATH`: output markdown path (default `report.md`)
- `--model NAME`: override OpenAI model (default `gpt-4o-mini`)
- `--rfp-path PATH`: path to the RFP DOCX (required unless using the special phrase)

### What the agent does
1. Parses the RFP DOCX and extracts important criteria/questions using heuristics (evaluation criteria, SLAs, KPIs, technical/commercial/compliance sections, numbered lists, and tables).
2. Crafts a web search query guided by top RFP items and gathers evidence from the web only.
3. Produces a Markdown bid draft with, for each RFP item:
   - A concise answer tailored to tender.io's capabilities.
   - A short explanation describing what web research was performed and why it supports the answer.
   - Inline citations like [1], [2], etc., with a final "Sources" list mapping numbers to URLs.

### Notes
- `.env` and `data/raw/` are ignored by git. Do not commit keys or RFPs.
- If a site blocks requests, the page may be skipped; the agent continues with remaining sources.
- Supported local formats for RFP: DOCX (others can be added on request).
