from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import settings


class LLMClient:
	def __init__(self, api_key: str | None = None, model: str | None = None):
		self.client = OpenAI(api_key=api_key or settings.openai_api_key)
		self.model = model or settings.default_model

	def summarize(self, query: str, notes: List[str]) -> str:
		joined = "\n\n".join(notes)
		prompt = (
			"You are a meticulous research assistant. Given a user query and a set of extracted notes, "
			"write a concise synthesis (bulleted if helpful) with inline citations like [1], [2], "
			"and end with a Sources list mapping numbers to URLs. Only cite what is supported by the notes."
		)
		messages = [
			{"role": "system", "content": prompt},
			{
				"role": "user",
				"content": f"Query: {query}\n\nNotes:\n{joined}\n\nReturn: Synthesis with inline citations and a sources list.",
			},
		]
		resp = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.2)
		return resp.choices[0].message.content or ""

	def write_bid_with_explanations(self, rfp_items: List[str], notes: List[str], company_context: str = "tender.io") -> str:
		joined_notes = "\n\n".join(notes)
		joined_rfp = "\n".join(f"- {it}" for it in rfp_items)
		system = (
			"You are a bid-writing assistant for tender.io."
			" Extract the RFP requirements and provide for each: (1) a concise answer, (2) a brief explanation of what research you did and why it supports the answer,"
			" and (3) inline citations like [1], [2] referencing the Sources list. End with 'Sources' mapping numbers to URLs."
		)
		user = (
			f"RFP Items (summarize & answer each):\n{joined_rfp}\n\n"
			f"Evidence Notes (local docs + web):\n{joined_notes}\n\n"
			"Return a structured markdown with headings per RFP item, followed by an overall executive summary."
		)
		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		]
		resp = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.2)
		return resp.choices[0].message.content or ""
