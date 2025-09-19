from __future__ import annotations

from pathlib import Path
from typing import List, Dict
import re

from docx import Document

from .schema import SupplierResponseSchema

KEY_TERMS = [
	"requirement",
	"requirements",
	"evaluation",
	"criteria",
	"question",
	"questions",
	"scope",
	"deliverable",
	"service levels",
	"sla",
	"kpi",
	"technical",
	"commercial",
	"compliance",
]

HEADING_PATTERNS = [
	r"^\s*(section|part|chapter|appendix)\s+\d+\b",
	r"^\s*\d+(\.\d+)*\s+[A-Z][A-Za-z]",
	r"^\s*[A-Z][A-Z\s]{4,}$",
]
DATE_PATTERNS = [
	r"\b(\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b",
	r"\b(valid (from|until)|deadline|submission date)\b",
]
BOILERPLATE_TERMS = [
	"confidential",
	"copyright",
	"all rights reserved",
	"table of contents",
	"document control",
	"revision history",
]


def _looks_like_heading(text: str) -> bool:
	t = text.strip()
	if not t:
		return False
	for p in HEADING_PATTERNS:
		if re.search(p, t, flags=re.IGNORECASE):
			return True
	return False


def _looks_like_date_or_boilerplate(text: str) -> bool:
	t = text.strip().lower()
	if not t:
		return False
	for p in DATE_PATTERNS:
		if re.search(p, t, flags=re.IGNORECASE):
			return True
	if any(term in t for term in BOILERPLATE_TERMS):
		return True
	return False


def _is_candidate_line(text: str) -> bool:
	t = text.strip()
	if not t:
		return False
	if _looks_like_heading(t) or _looks_like_date_or_boilerplate(t):
		return False
	low = t.lower()
	if any(k in low for k in KEY_TERMS):
		return True
	# numbered/bulleted list heuristics (but avoid pure headings)
	if re.match(r"^\s*(\d+\.|[\-\*•])\s+", t):
		return True
	return False


def _preprocess_text(text: str) -> str:
	# Remove dates/boilerplate and collapse whitespace
	if _looks_like_heading(text) or _looks_like_date_or_boilerplate(text):
		return ""
	text = re.sub(r"\s+", " ", text)
	return text.strip()


def extract_criteria_from_docx(path: Path, max_items: int = 20) -> List[str]:
	doc = Document(str(path))
	lines: List[str] = []
	for p in doc.paragraphs:
		text = _preprocess_text(p.text or "")
		if text and _is_candidate_line(text):
			lines.append(text)
	for table in doc.tables:
		for row in table.rows:
			for c in row.cells:
				text = _preprocess_text(c.text or "")
				if text and _is_candidate_line(text):
					lines.append(text)
	seen = set()
	unique: List[str] = []
	for ln in lines:
		k = ln.lower()
		if k in seen:
			continue
		seen.add(k)
		unique.append(ln)
	return unique[:max_items]


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
	"capabilities": ["feature", "function", "capability", "workflow", "report"],
	"integrations": ["integration", "api", "sso", "single sign-on", "erp", "crm"],
	"users_roles": ["user", "role", "permission", "access", "admin"],
	"security": ["security", "gdpr", "iso", "encryption", "data protection", "backup"],
	"commercials": ["price", "pricing", "cost", "license", "contract", "sla"],
	"delivery": ["implementation", "timeline", "migration", "training", "onboarding"],
	"support": ["support", "helpdesk", "ticket", "response", "uptime"],
	"evidence": ["case study", "reference", "evidence", "proof", "example"],
	"submission": ["submission", "format", "appendix", "document", "response"],
	"partnership": ["partner", "partnership", "collaborat", "account management", "governance"],
}


def categorize_to_schema(items: List[str]) -> SupplierResponseSchema:
	schema = SupplierResponseSchema()
	for it in items:
		low = it.lower()
		assigned = False
		for field, kws in CATEGORY_KEYWORDS.items():
			if any(kw in low for kw in kws):
				getattr(schema, field).append(it)
				assigned = True
				break
		if not assigned:
			# default bucket
			schema.capabilities.append(it)
	return schema
