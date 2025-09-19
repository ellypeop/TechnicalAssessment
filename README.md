## Research Agent

A research and bid-writing assistant for tender.io. It ingests RFP documents (DOCX), performs targeted web research, and produces a concise, cited Markdown report. Keys are loaded from `.env`.

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

3. Ensure your `.env` at the project root contains relevant keys, e.g.:
```
OPENAI_API_KEY=...
SERPAPI_API_KEY=...      # optional, enables Google via SerpAPI
```

### Usage

General research (local docs + web):
```bash
python -m research_agent.cli "summarize key requirements for bid management systems"
```

Bid-writing mode (parse RFP and generate answers with explanations and citations):
- The RFP file is used solely to extract the questions/criteria.
- Answers and citations are derived from web sources only (the RFP is not cited).
- You can explicitly enable with `--bid --rfp-path PATH_TO_RFP.docx`, or use the phrase: "write a bid for the RFP stored in file".

Examples:
```bash
python -m research_agent.cli "Write a bid for the RFP stored in file" --out bid.md
python -m research_agent.cli --bid --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --max-results 8 --out bid_samsic.md
```

Options:
- `--max-results INT`: number of web search results to consider (default 8)
- `--out PATH`: output markdown path (default `report.md`)
- `--model NAME`: override OpenAI model (default `gpt-4o-mini`)
- `--include-samsic/--no-include-samsic`: include the default Samsic RFP DOCX (default on) for general research mode
- `--doc PATH`: add additional local documents (repeatable). Currently DOCX is supported.
- `--local-max-chunks INT`: cap the number of local document chunks to include (default 3)
- `--bid`: enable bid-writing mode
- `--rfp-path PATH`: path to the RFP DOCX for bid-writing mode

### What the agent does in bid mode
1. Parses the RFP DOCX and extracts important criteria/questions using heuristics (evaluation criteria, SLAs, KPIs, technical/commercial/compliance sections, numbered lists, and tables).
2. Crafts a web search query guided by top RFP items and gathers evidence from the web only.
3. Produces a Markdown bid draft with, for each RFP item:
   - A concise answer appropriate for a bid response.
   - A brief explanation describing what research was performed and why it supports the answer.
   - Inline citations like [1], [2], etc., with a final "Sources" list mapping numbers to URLs.

### Notes
- Keys are read from `.env`. Only `OPENAI_API_KEY` is required to run.
- If a site blocks requests, the page may be skipped; the agent continues with remaining sources.
- Supported local formats: DOCX (others can be added on request).
