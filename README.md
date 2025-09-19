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
- Refactored project allowed to elect flags for different responses (generic, document based etc) however needed to refactor again so agent would use document to derive questions and use web search to provide responses
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
- Terminal command to produce versioned report "python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --max-results 8 --versioned"

### Version 13:38pm

- Only used Tender.io as a web search source
- Questions 2, 3, 4, 5, 6, 8, 9 shouldn't be considered a criteria for a question

Overall evaluation is the output is fairly poor and doesn't capture what the essential criteria is in the document to be responded to. Will tweak the prompt to see if this improves output:

Current Prompt:

			"You are a bid-writing assistant for tender.io."
			" For each extracted RFP requirement, produce: (1) a concise, customer-focused answer tailored for tender.io's capabilities,"
			" (2) a short explanation describing what web research you performed and why it supports the answer, and"
			" (3) inline citations like [1], [2] referencing the Sources list."
			" Use only information supported by the evidence notes."

Refined Prompt:

			"You are an experienced bid-writing assistant for tender.io."
			" You must read the RFP and determine which are the essential RFP requirments that require a response"
      " For each extracted RFP requirement, produce: (1) a concise, customer-focused answer tailored for tender.io's capabilities,"
			" a short explanation describing what web research you performed and why it supports the answer, and"
			" inline citations like [1], [2] referencing the Sources list."
			" Use only information supported by the evidence notes."

### Version 13:48pm

- Still struggling to capture what is essential criteria, will see if upgrading to a better model will improve performance.

command used: python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --max-results 8 --versioned --model NAME "o3-pro" # reasoning focused

### Version 13:56pm

- Again still struggling to capture that the essential critera is. will sense check with Chat GPT 5 by providing it the document and see whether it can succesfully extract the criteria to research

#### Human Evaluation of RFP

- Integration with internal systems
- Ability to import exisiting bid library
- AI-driven content generation and web-based access
- 5 super user accounts (for project managers and bid managers)
- 10 additiona users with permissions to review content and create smaller proposals
- Key features and highlights of the system
- Tangible benefits to Samsic
- Integration capabitilies with existing tools (Microsoft Teams, Shared Drives, Salesforce)
- Licensing model and cost breakdown
- ROI examples
- Proposed implementation approach and timeline
- Ongoing support and maintenance services
- Relevant case studies and two client refeences
- Long term partner with seamless ingegration into exising systems, workflows, and evolve with the buisness

Should be noted the assitant should also pick up addtional context to consider and not answer, for example ensuring they responses are GDPR compliant. 

#### Chat GPT5 Evaluation of RFP
"Prompt: Analyse the attached document and define what the essentially criteria is to be researched and answered for a tender" - provide your response in concise bullet points"

Answer:

##### System Capabilities
- Integration with Samsic UK’s internal systems (e.g. Microsoft Teams, Shared Drives, Salesforce).
- Import of existing bid library.
- AI-driven content generation.
- Web-based access.
- User accounts: 5 super users, 10 additional users.
##### Presentation Requirements
- Key features and highlights of the system.
- Tangible benefits to Samsic UK.
- Licensing model and detailed cost breakdown.
- Return on Investment (ROI) examples.
- Implementation approach and timeline.
- Ongoing support and maintenance services.
- Case studies and 2 client references.
##### Compliance & Security
- Adherence to UK GDPR and Data Protection Act 2018.
- Clear data handling, storage, retention, and encryption practices.
##### Commercial & Contractual
- Long-term partnership potential and platform scalability.
- Ability to meet tender deadlines (submission by 16th September 2025).
- Costs borne by tendering contractor; Samsic reserves negotiation and selection rights.

Chat GPT 5 is successful at capturing the relevant information, will see what it recommends to try and get the research Assitant to be more effective. 

Chat GPT highlights the agent is fed headings rather than a structured extraction of asks and that the prompt doesn't enforce a schema.

Refactor in Cursor and request the follow:

- The current LLM output is over-focusing on headings and dates rather than the actual requirements.
- Implement a JSON schema that captures the essential supplier response items (capabilities, integrations, users/roles, security, commercials, delivery, support, evidence, submission, partnership).
- Add preprocessing on the RFP text to strip or down-weight headings, dates, and boilerplate so they do not dominate extraction.
- Ensure the model only extracts requirements that suppliers must answer, not general context or section titles.

Produced a new schema.py file

### Version 14:25pm

- Still missing the essential criteria, focusing on being shortlisted, doing a presentation and the expected timeline
- Hasn't used the tender.io website at all for its response

It's still treating headings as requirements, incorrect data filters treat dates as items, the web search is built from noisy lines and not a schema, the prompt does not specify to ignore headings
Pushing current version to github and implementing code changes provided by ChatGPT5 (changes made to agent.py, llm.py, rfp.py)

### Version 14:48pm

- The questions are better however its web search explanation is note detailed "This requirement is directly stated in the RFP items." and does not research tender.io
- The prompt erroneously guides the LLM to not use its own prior knowledge

Cursor Prompt to refactor the codebase so it effectively researches the web, including searching tender.io information, to provide a response:

"refactor the code base to address the issue that the agent does not do a web search on tender.io (and other general website when nessecary) to provide an informed response to the questions generated in the report"

Need to refactor again after this as the prompt is still ineffective

### Version 14:59pm

- Still stating "This requirement is directly stated in the RFP items." so need to ammend the prompt to be less restrictive, is also still not using tender.io to respond.

Refactoring so the LLM.py file is less restrictive and priortisies searching tender.io before providing a response.

### Version 15:07pm

- The questions are somewhat improved however the answers are generic and in the voice of Samsic UK not tender.io. Need to refactor again to emphasise that responses must include web searches into tender.io
- should also be noted that the websearches keep brining up the same chinese website - https://zhidao.baidu.com/ - this may be what was causing issue as I hadn't stated mytender.io instead saying tender.io


### Version 15:20pm

- The responses are mytender.io specific however they are still fairly general with the agent not exploring directory roots of the mytender.io website for more detailed responses. The questions are much better and have succesfully extracted the meaningful aspects of the RFP.

## Final Thoughts

- To improve the model response still we'd want to enable the agent to use all webpages within mytender.io to formulate a response
- We'd also want to be able to succesfully balance the agents ability to use general websites as the groundwork for a response with the mytender.io website being used to answer specific details related to mytender.io
- Once the above can be succesfully implemented/balanced - explore how using different models can improve output
- General refaxctoring of the prompt schema and exploring other tools the agent can use to modify the response would also be beneficial

## Research Agent (tender.io Bid Assistant)

A bid-writing assistant for tender.io. It parses an RFP document (DOCX), performs targeted web research on tender.io only, and produces a concise Markdown bid draft with explanations and inline citations to tender.io sources. Keys are loaded from `.env`.

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

The agent uses the RFP file solely to extract the questions/criteria. Answers and citations are derived from tender.io web sources only.

Examples:
```bash
python -m research_agent.cli --rfp-path "data/raw/RFP - Bid Management Systems - Samsic UK.docx" --versioned
```

Options:
- `--max-results INT`: number of queries for broader seeding (still tender.io-only)
- `--out PATH`: output markdown path (default `report.md`)
- `--model NAME`: override OpenAI model (default `gpt-4o-mini`)
- `--rfp-path PATH`: path to the RFP DOCX (required unless using the special phrase)
- `--versioned/--no-versioned`: save timestamped versions under `reports/` and update `reports/bid_latest.md`

### What the agent does
1. Parses the RFP DOCX and extracts actionable supplier requirements with preprocessing to ignore headings, dates, and boilerplate.
2. Categorises requirements to a supplier-response schema (capabilities, integrations, users/roles, security, commercials, delivery, support, evidence, submission, partnership).
3. Searches tender.io only (site:tender.io) with per-item queries plus a small seed of tender.io-focused queries to gather evidence.
4. Produces a Markdown bid draft with for each requirement: a concise response, an explanation of the tender.io research used, and inline citations like [1], [2] with a Sources list of tender.io URLs.

### Notes
- `.env` and `data/raw/` are ignored by git. Do not commit keys or RFPs.
- If a tender.io page blocks requests, it may be skipped; the agent continues with remaining tender.io sources.
- Supported local formats for RFP: DOCX (others can be added on request).
