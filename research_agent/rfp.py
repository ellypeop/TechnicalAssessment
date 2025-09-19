from __future__ import annotations

from pathlib import Path
from typing import List

from docx import Document

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


def _is_candidate_line(text: str) -> bool:
	t = text.strip().lower()
	if not t:
		return False
	if any(k in t for k in KEY_TERMS):
		return True
	# numbered/bulleted list heuristics
	if t[0:2].isdigit() or t.startswith(('-', '*')):
		return True
	return False


def extract_criteria_from_docx(path: Path, max_items: int = 20) -> List[str]:
	doc = Document(str(path))
	lines: List[str] = []
	# paragraphs
	for p in doc.paragraphs:
		text = (p.text or "").strip()
		if _is_candidate_line(text):
			lines.append(text)
	# simple table scan
	for table in doc.tables:
		for row in table.rows:
			cells = [c.text.strip() for c in row.cells]
			for c in cells:
				if _is_candidate_line(c):
					lines.append(c)
	# de-dup and trim
	seen = set()
	unique: List[str] = []
	for ln in lines:
		k = ln.lower()
		if k in seen:
			continue
		seen.add(k)
		unique.append(ln)
	return unique[:max_items]
