from __future__ import annotations

from typing import List, Dict
from pydantic import BaseModel, Field


class SupplierResponseSchema(BaseModel):
	capabilities: List[str] = Field(default_factory=list)
	integrations: List[str] = Field(default_factory=list)
	users_roles: List[str] = Field(default_factory=list)
	security: List[str] = Field(default_factory=list)
	commercials: List[str] = Field(default_factory=list)
	delivery: List[str] = Field(default_factory=list)
	support: List[str] = Field(default_factory=list)
	evidence: List[str] = Field(default_factory=list)
	submission: List[str] = Field(default_factory=list)
	partnership: List[str] = Field(default_factory=list)

	def to_nonempty_dict(self) -> Dict[str, List[str]]:
		return {k: v for k, v in self.model_dump().items() if isinstance(v, list) and v}
