from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import settings


class LLMClient:
	def __init__(self, api_key: str | None = None, model: str | None = None):
		self.client = OpenAI(api_key=api_key or settings.openai_api_key)
		self.model = model or settings.default_model

	def write_bid_with_explanations(self, rfp_items: List[str], notes: List[str], company_context: str = "mytender.io") -> str:
		joined_notes = "\n\n".join(notes)
		joined_rfp = "\n".join(f"- {it}" for it in rfp_items)
		system = (
			"You are a bid-writing assistant for mytender.io."
			" Answer supplier requirements extracted from an RFP."
			" Use only the provided evidence notes which come from mytender.io pages."
			" STRICT RULES:"
			" - Cite only mytender.io URLs in inline citations and Sources."
			" - If an evidence note is not from mytender.io, ignore it."
			" - If evidence is insufficient for a requirement, state assumptions and clearly mark gaps."
		)
		user = (
			f"RFP Requirements (answer each in order):\n{joined_rfp}\n\n"
			f"Numbered Evidence Notes (mytender.io only):\n{joined_notes}\n\n"
			"Output format (Markdown):\n"
			"- A short Executive Summary\n"
			"- For each requirement: a 'Response' paragraph, an 'Explanation of Research' paragraph (describe mytender.io pages used), and inline citations.\n"
			"- Finish with 'Sources' mapping citation numbers to mytender.io URLs only."
		)
		messages = [
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		]
		resp = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.3)
		return resp.choices[0].message.content or ""
