from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set
from pathlib import Path
from urllib.parse import urlparse

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


def _is_allowed_url(url: str, allowed_suffixes: List[str]) -> bool:
	try:
		host = urlparse(url).hostname or ""
		host = host.lower()
		return any(host == s or host.endswith("." + s) for s in allowed_suffixes)
	except Exception:
		return False


class ResearchAgent:
	def __init__(self):
		self.search = get_default_search_provider()
		self.llm = LLMClient()
		self.allowed_domains = ["mytender.io", "www.mytender.io"]

	def _collect_company_evidence(self, domains: List[str], max_results: int = 10) -> List[Evidence]:
		"""
		Collect seed evidence strictly from mytender.io (first-party) domains.
		"""
		seeds: List[str] = []
		for d in domains:
			seeds.extend([
				f"site:{d} bid management",
				f"site:{d} features OR capabilities",
				f"site:{d} integration OR API OR Microsoft Teams OR Salesforce OR SSO",
				f"site:{d} security OR GDPR OR encryption OR data protection OR retention",
				f"site:{d} pricing OR license OR licensing OR cost",
				f"site:{d} support OR SLA OR uptime OR maintenance",
				f"site:{d} case study OR customer OR reference",
			])

		out: List[Evidence] = []
		seen: Set[str] = set()
		for q in seeds:
			if len(out) >= max_results:
				break
			try:
				for r in self.search.search(q, max_results=2):
					if len(out) >= max_results:
						break
					if r.url in seen or not _is_allowed_url(r.url, self.allowed_domains):
						continue
					html = fetch_url(r.url)
					text = extract_readable_text(html, base_url=r.url)
					if not text:
						continue
					seen.add(r.url)
					out.append(Evidence(index=0, title=r.title, url=r.url, snippet=r.snippet, text=text))
			except Exception:
				continue
		return out[:max_results]

	def _collect_per_item_company_evidence(
		self,
		items: List[str],
		domains: List[str],
		per_item_company: int = 2,
	) -> List[Evidence]:
		"""
		For each RFP item, perform focused searches ONLY on mytender.io domains.
		"""
		collected: List[Evidence] = []
		seen: Set[str] = set()
		for it in items:
			for d in domains:
				q = f"site:{d} {it}"
				try:
					for r in self.search.search(q, max_results=per_item_company):
						if r.url in seen or not _is_allowed_url(r.url, self.allowed_domains):
							continue
						html = fetch_url(r.url)
						text = extract_readable_text(html, base_url=r.url)
						if not text:
							continue
						seen.add(r.url)
						collected.append(Evidence(index=0, title=r.title, url=r.url, snippet=r.snippet, text=text))
				except Exception:
					continue
		return collected

	def write_bid_for_rfp(
		self,
		rfp_path: Path,
		max_results: int = 12,
	) -> tuple[str, List[str], List[Evidence]]:
		# 1) Extract actionable items and categorise into schema
		raw_items = extract_criteria_from_docx(rfp_path, max_items=50)
		schema: SupplierResponseSchema = categorize_to_schema(raw_items)

		# 2) Build ordered items (priority buckets)
		priority_fields = [
			"capabilities",
			"integrations",
			"users_roles",
			"commercials",
			"delivery",
			"support",
			"security",
			"evidence",
			"submission",
			"partnership",
		]
		rfp_items_ordered: List[str] = []
		for f in priority_fields:
			rfp_items_ordered.extend(getattr(schema, f))

		# 3) Collect ONLY mytender.io evidence (seed + per-item)
		company_domains = ["mytender.io", "www.mytender.io"]
		seed_evidence = self._collect_company_evidence(domains=company_domains, max_results=6)
		per_item_evidence = self._collect_per_item_company_evidence(
			items=rfp_items_ordered,
			domains=company_domains,
			per_item_company=2,
		)

		# 4) Combine, deduplicate, and reindex evidence
		all_evidence: List[Evidence] = []
		seen_urls: Set[str] = set()
		for ev in seed_evidence + per_item_evidence:
			if ev.url in seen_urls or not _is_allowed_url(ev.url, self.allowed_domains):
				continue
			seen_urls.add(ev.url)
			all_evidence.append(ev)
		for i, e in enumerate(all_evidence, start=1):
			e.index = i

		# 5) Prepare notes and generate the bid
		notes = [f"[{e.index}] {e.title} — {e.url}\n\n{e.text[:4000]}" for e in all_evidence]
		bid_md = self.llm.write_bid_with_explanations(
			rfp_items=rfp_items_ordered,
			notes=notes,
			company_context="mytender.io",
		)
		return bid_md, raw_items, all_evidence
