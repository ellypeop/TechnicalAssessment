from __future__ import annotations

from dataclasses import dataclass
from typing import List
from pathlib import Path

from .search import get_default_search_provider, SearchResult
from .fetch import fetch_url, extract_readable_text
from .llm import LLMClient
from .rfp import extract_criteria_from_docx


@dataclass
class Evidence:
	index: int
	title: str
	url: str
	snippet: str
	text: str


class ResearchAgent:
	def __init__(self):
		self.search = get_default_search_provider()
		self.llm = LLMClient()

	def _collect_web_evidence(self, query: str, max_results: int = 8) -> List[Evidence]:
		web_candidates: List[Evidence] = []
		results: List[SearchResult] = self.search.search(query, max_results=max_results)
		for i, r in enumerate(results, start=1):
			try:
				html = fetch_url(r.url)
				text = extract_readable_text(html, base_url=r.url)
				if not text:
					continue
				web_candidates.append(Evidence(index=i, title=r.title, url=r.url, snippet=r.snippet, text=text))
			except Exception:
				continue
		return web_candidates

	def write_bid_for_rfp(
		self,
		rfp_path: Path,
		max_results: int = 8,
	) -> tuple[str, List[str], List[Evidence]]:
		# 1) Extract criteria/questions from the RFP
		rfp_items = extract_criteria_from_docx(rfp_path, max_items=20)
		# 2) Build an aggregated query from top RFP items to guide web search
		agg_terms = " ".join(rfp_items[:6]) if rfp_items else "Bid management systems UK facilities management requirements"
		query = f"Evidence and best practices for: {agg_terms}"
		# 3) Collect evidence using WEB ONLY (RFP is used only to extract questions)
		evidence = self._collect_web_evidence(query=query, max_results=max_results)
		# 4) Prepare notes for LLM bid generation
		notes = [f"[{e.index}] {e.title} — {e.url}\n\n{e.text[:4000]}" for e in evidence]
		bid_md = self.llm.write_bid_with_explanations(rfp_items=rfp_items, notes=notes, company_context="tender.io")
		return bid_md, rfp_items, evidence
