from __future__ import annotations

from dataclasses import dataclass
from typing import List

from duckduckgo_search import DDGS
try:
	from serpapi import GoogleSearch  # type: ignore
except Exception:  # pragma: no cover
	GoogleSearch = None  # type: ignore

from .config import settings


@dataclass
class SearchResult:
	url: str
	title: str
	snippet: str


class SearchProvider:
	def search(self, query: str, max_results: int = 8) -> List[SearchResult]:
		raise NotImplementedError


class DuckDuckGoProvider(SearchProvider):
	def search(self, query: str, max_results: int = 8) -> List[SearchResult]:
		results: List[SearchResult] = []
		with DDGS() as ddgs:
			for item in ddgs.text(query, max_results=max_results, safesearch="moderate"):
				url = item.get("href") or item.get("url") or ""
				title = item.get("title") or ""
				snippet = item.get("body") or item.get("snippet") or ""
				if not url:
					continue
				results.append(SearchResult(url=url, title=title, snippet=snippet))
		return results


class SerpApiProvider(SearchProvider):
	def __init__(self, api_key: str):
		self.api_key = api_key

	def search(self, query: str, max_results: int = 8) -> List[SearchResult]:
		if GoogleSearch is None:
			raise RuntimeError("serpapi is not installed")
		params = {
			"engine": "google",
			"q": query,
			"api_key": self.api_key,
			"num": min(max_results, 10),
		}
		search = GoogleSearch(params)
		data = search.get_dict()
		organic = data.get("organic_results", [])
		results: List[SearchResult] = []
		for item in organic[:max_results]:
			url = item.get("link") or ""
			title = item.get("title") or ""
			snippet = item.get("snippet") or ""
			if url:
				results.append(SearchResult(url=url, title=title, snippet=snippet))
		return results


def get_default_search_provider() -> SearchProvider:
	if settings.serpapi_api_key:
		return SerpApiProvider(settings.serpapi_api_key)
	return DuckDuckGoProvider()
