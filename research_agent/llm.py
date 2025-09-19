from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import settings


class LLMClient:
	def __init__(self, api_key: str | None = None, model: str | None = None):
		self.client = OpenAI(api_key=api_key or settings.openai_api_key)
		self.model = model or settings.default_model

	def write_bid_with_explanations(self, rfp_items: List[str], notes: List[str], company_context: str = "tender.io") -> str:
		joined_notes = "\n\n".join(notes)
		joined_rfp = "\n".join(f"- {it}" for it in rfp_items)
		system = (
			"You are an experienced bid-writing assistant for tender.io."
			" You must read the RFP and determine which are the essential RFP requirments that require a response"
			" For each extracted RFP requirement, produce: (1) a concise, customer-focused answer tailored for tender.io's capabilities,"
			" a short explanation describing what web research you performed and why it supports the answer, and"
			" inline citations like [1], [2] referencing the Sources list."
			" Use only information supported by the evidence notes."
		)
		user = (
			f"RFP Items (answer each):\n{joined_rfp}\n\n"
			f"Web Evidence Notes (no RFP text):\n{joined_notes}\n\n"
			"Return structured Markdown with a heading per RFP item, followed by an executive summary and a final Sources list mapping numbers to URLs."
		)
		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		]
		resp = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.2)
		return resp.choices[0].message.content or ""
