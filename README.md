## Notes and Steps Taken to Set Up Agent

- Initial set up included complex prompt to ChatGPT 5 to aid with coding and advice on setting up research asssitant
- Provided complex prompt to give to Cursor to set up Research Assistant
- Cursor was stuck on command lines, too much too soon - overly complex
- Restarted and gave Cursor simple directive to set up research assitant. Inital project contained one python file for the agent plus a requirements.txt and ReadMe
- Created new ChatGPT 5 conversation to focus more on advise and less on code
- Cursor generated basic research assitant with output in terminal. Used ChatGPT 5 to add addtional building blocks (web search coupled with document extraction and output in JSON/Markdown) - issues arose with ineffective code refactoring resulting in no output being given
- Started project again in Cursor requesting Research Assitant, this time it created a more sophisticated version with seperate python files to handle different tasks and automatically produced output in Markdown
- Did multiple refactors within Cursor to include :
     - Hybrid look up of documents and web searches
     - Ammend the LLM prompt from generic to specific to tender.io
- Refactored project allowed to elect flags for different responses (generic, document based etc) however needed to refactor again so agent would use document to dervie questions and use web search to provide responses
- Final refactors to reformat the assitant inline with assessment prompt:
     - it is a research assistant for the company tender.io to assist them in writing bids to clients
     - it will be given an RFP document (data/raw/RFP - Bid Management Systems - Samsic UK.docx
     - it needs to extract the important criteria from the document and conduct research online to answer these questions
     - it should provide an example answer along with an explanation to the user on what research it did and why it chose it
     - it should write concise synthesis (with inline citations like [1], [2] and end with a Sources list mapping numbers to URLs. Only cite what is supported by the notes.)
     - the output should be stored in the markdown file
     - the user input should specify “write a bid for the RFP stored in file” - this should be explained clearly in the read me
- Output showed it only using document to produce response and not web search. Refactored Cursor again to fix this so output dervied from web searches
- Tidied up code base to remove redundant flags/generic responses/previous markdown files generated
- Added sensitive information to .gitignore (Keys and Internal Documents)
- Version 1 of Research Assitant set up. Takes prompt to start research, derives questions from RFP document, uses web search to produce answers and provide explanations
- Pushed on to Github to utilise versioning during evaulation phase

## Evaluation & Analysis
- Additional refactor; implement versioning of the bid.md file to compare outputs after model changes


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

Examples:
```bash
python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --max-results 8 --out bid.md
# or use the special phrase
python -m research_agent.cli "Write a bid for the RFP stored in file" --out bid.md
```

Options:
- `--max-results INT`: number of web search results to consider (default 8)
- `--out PATH`: output markdown path (default `report.md`)
- `--model NAME`: override OpenAI model (default `gpt-4o-mini`)
- `--rfp-path PATH`: path to the RFP DOCX (required unless using the special phrase)
- `--versioned/--no-versioned`: save timestamped versions under `reports/` and update `reports/bid_latest.md`

### Versioned outputs and diffs
- Save a timestamped bid and update the latest copy:
```bash
python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --versioned
```
- Diff the two most recent bids:
  - PowerShell:
    ```powershell
    ./scripts/diff_latest_bids.ps1
    ```
  - Bash:
    ```bash
    bash scripts/diff_latest_bids.sh
    ```

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
