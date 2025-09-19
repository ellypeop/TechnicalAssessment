from __future__ import annotations

from dataclasses import dataclass
from typing import List
from pathlib import Path

from .search import get_default_search_provider, SearchResult
from .fetch import fetch_url, extract_readable_text
from .llm import LLMClient
from .rfp import extract_criteria_from_docx, categorize_to_schema
from .schema import SupplierResponseSchema


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
		# 1) Extract raw candidate items and categorize to schema
		raw_items = extract_criteria_from_docx(rfp_path, max_items=50)
		schema: SupplierResponseSchema = categorize_to_schema(raw_items)
		# Derive prioritized query terms from schema buckets (capabilities, security, commercials, etc.)
		priority_fields = [
			"capabilities",
			"security",
			"integrations",
			"users_roles",
			"commercials",
			"delivery",
			"support",
			"evidence",
			"submission",
			"partnership",
		]
		focus_terms: List[str] = []
		for f in priority_fields:
			focus_terms.extend(getattr(schema, f)[:3])
		
		agg_terms = " ".join(focus_terms[:10]) if focus_terms else "Bid management systems UK facilities management requirements"
		query = f"Supplier responses and best practices for: {agg_terms}"

		# 2) Collect evidence using WEB ONLY
		evidence = self._collect_web_evidence(query=query, max_results=max_results)
		# 3) Prepare notes for LLM bid generation using all evidence
		notes = [f"[{e.index}] {e.title} — {e.url}\n\n{e.text[:4000]}" for e in evidence]
		# Flatten schema back to ordered list of RFP items for per-item answering
		rfp_items_ordered: List[str] = []
		for f in priority_fields:
			rfp_items_ordered.extend(getattr(schema, f))
		bid_md = self.llm.write_bid_with_explanations(rfp_items=rfp_items_ordered, notes=notes, company_context="tender.io")
		return bid_md, raw_items, evidence
