from __future__ import annotations

import re
from typing import Optional

import requests
import trafilatura
from bs4 import BeautifulSoup
from readability import Document

from .config import settings


def fetch_url(url: str, timeout: Optional[int] = None) -> str:
	t = timeout or settings.request_timeout_seconds
	headers = {"User-Agent": settings.user_agent}
	resp = requests.get(url, headers=headers, timeout=t)
	resp.raise_for_status()
	return resp.text


def extract_readable_text(html: str, base_url: str = "") -> str:
	text = trafilatura.extract(html, url=base_url, favor_recall=True, include_comments=False) or ""
	if text.strip():
		return _normalize_whitespace(text)

	doc = Document(html)
	summary_html = doc.summary(html_partial=True)
	soup = BeautifulSoup(summary_html, "lxml")
	text = soup.get_text(separator="\n")
	if text.strip():
		return _normalize_whitespace(text)

	soup = BeautifulSoup(html, "lxml")
	text = soup.get_text(separator="\n")
	return _normalize_whitespace(text)


def _normalize_whitespace(text: str) -> str:
	text = re.sub(r"\s+", " ", text)
	return text.strip()
