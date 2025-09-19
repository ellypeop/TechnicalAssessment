from __future__ import annotations

from dataclasses import dataclass
from typing import List
from pathlib import Path

from .search import get_default_search_provider, SearchResult
from .fetch import fetch_url, extract_readable_text
from .llm import LLMClient
from .local_docs import extract_docx_text
from .rfp import extract_criteria_from_docx


@dataclass
class Evidence:
	index: int
	title: str
	url: str
	snippet: str
	text: str


def _chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
	chunks: List[str] = []
	text = text.strip()
	if not text:
		return chunks
	start = 0
	length = len(text)
	while start < length:
		end = min(start + max_chars, length)
		chunk = text[start:end].strip()
		if chunk:
			chunks.append(chunk)
		if end >= length:
			break
		start = max(end - overlap, end)
	return chunks


class ResearchAgent:
	def __init__(self):
		self.search = get_default_search_provider()
		self.llm = LLMClient()

	def run(
		self,
		query: str,
		max_results: int = 8,
		local_docs: List[Path] | None = None,
		local_max_chunks: int = 3,
	) -> tuple[str, List[Evidence]]:
		local_candidates: List[Evidence] = []
		# Ingest and chunk local documents
		for p in (local_docs or []):
			try:
				text = ""
				if p.suffix.lower() in {".docx", ".doc"}:
					text = extract_docx_text(p)
				if not text:
					continue
				title = p.stem.replace("_", " ")
				url = str(p.resolve())
				chunks = _chunk_text(text)
				for c in chunks:
					local_candidates.append(Evidence(index=0, title=title, url=url, snippet="(local document)", text=c))
			except Exception:
				continue

		# Web search and fetching
		web_candidates: List[Evidence] = []
		results: List[SearchResult] = self.search.search(query, max_results=max_results)
		for r in results:
			try:
				html = fetch_url(r.url)
				text = extract_readable_text(html, base_url=r.url)
				if not text:
					continue
				web_candidates.append(Evidence(index=0, title=r.title, url=r.url, snippet=r.snippet, text=text))
			except Exception:
				continue

		# Interleave: prioritize ensuring web sources appear; cap local by local_max_chunks
		selected: List[Evidence] = []
		local_used = 0
		li = 0
		wi = 0
		while wi < len(web_candidates) or (li < len(local_candidates) and local_used < local_max_chunks):
			# Always take a web candidate if available
			if wi < len(web_candidates):
				selected.append(web_candidates[wi])
				wi += 1
			# Then take a local candidate if under cap
			if li < len(local_candidates) and local_used < local_max_chunks:
				selected.append(local_candidates[li])
				li += 1
				local_used += 1

		# Assign indices
		for i, ev in enumerate(selected, start=1):
			ev.index = i

		notes = [f"[{e.index}] {e.title} — {e.url}\n\n{e.text[:4000]}" for e in selected]
		report = self.llm.summarize(query, notes)
		return report, selected

	def write_bid_for_rfp(
		self,
		rfp_path: Path,
		max_results: int = 8,
		local_max_chunks: int = 3,
	) -> tuple[str, List[str], List[Evidence]]:
		# 1) Extract criteria/questions from the RFP
		rfp_items = extract_criteria_from_docx(rfp_path, max_items=20)
		# 2) Build an aggregated query from top RFP items to guide web search
		agg_terms = " ".join(rfp_items[:6]) if rfp_items else "Bid management systems UK facilities management requirements"
		query = f"Evidence and best practices for: {agg_terms}"
		# 3) Collect evidence using WEB ONLY (RFP is used only to extract questions)
		_, evidence = self.run(query=query, max_results=max_results, local_docs=None, local_max_chunks=0)
		# 4) Prepare notes for LLM bid generation
		notes = [f"[{e.index}] {e.title} — {e.url}\n\n{e.text[:4000]}" for e in evidence]
		bid_md = self.llm.write_bid_with_explanations(rfp_items=rfp_items, notes=notes, company_context="tender.io")
		return bid_md, rfp_items, evidence
