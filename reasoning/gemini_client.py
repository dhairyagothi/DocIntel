from __future__ import annotations

import json
import re
from typing import Any

from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self._client = None
        if api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception:
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def generate_json(self, prompt: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self.available:
            return None
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=f"{prompt}\n\nINPUT:\n{json.dumps(payload, ensure_ascii=False, default=str)}",
                config={"response_mime_type": "application/json"},
            )
            text = getattr(response, "text", "") or ""
            fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
            return json.loads(fenced.group(1) if fenced else text)
        except Exception:
            return None