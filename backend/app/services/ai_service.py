import json
import re
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import requests
import groq
from backend.app.config import settings

logger = logging.getLogger("ai_service")
T = TypeVar("T", bound=BaseModel)

class AIService:
    def __init__(self):
        self.groq_client = groq.Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.google_api_key = settings.google_api_key

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _generate_google_gemini(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 8192, is_json: bool = False) -> Optional[str]:
        if not self.google_api_key:
            return None

        models = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
        for model_name in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.google_api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": 0.2
                    }
                }
                if system_prompt:
                    payload["systemInstruction"] = {
                        "parts": [{"text": system_prompt}]
                    }
                if is_json:
                    payload["generationConfig"]["response_mime_type"] = "application/json"

                response = requests.post(url, json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                else:
                    logger.warning(f"Google model {model_name} returned status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.warning(f"Google model {model_name} failed: {e}")
                continue
        return None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096, is_json: bool = False) -> str:
        # 1. Primary: Google Gemini 3.6 Flash / 3.5 Flash Lite (до 1M контекста, до 8192 токенов вывода)
        gemini_res = self._generate_google_gemini(prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens, is_json=is_json)
        if gemini_res:
            return gemini_res

        # 2. Secondary: Groq Cloud
        if self.groq_client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            models_to_try = ["qwen/qwen3.8-27b", "qwen/qwen3.6-27b"]
            for model_name in models_to_try:
                try:
                    kwargs = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": min(max_tokens, 950)
                    }
                    if is_json:
                        kwargs["response_format"] = {"type": "json_object"}

                    resp = self.groq_client.chat.completions.create(**kwargs)
                    content = resp.choices[0].message.content
                    if content:
                        return content
                except Exception as e:
                    logger.warning(f"Groq model {model_name} failed: {e}")
                    continue

        raise RuntimeError("Не удалось сгенерировать ответ через доступные AI провайдеры")

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None, max_tokens: int = 8192) -> T:
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)
        strict_system = (
            (system_prompt or "Ты — ведущий системный аналитик IT-компании Xpage.") +
            f"\n\nВАЖНО: Твой ответ ОБЯЗАН быть строго валидным JSON-объектом, соответствующим следующей JSON-схеме Pydantic:\n"
            f"{schema_json}\n\n"
            f"ПРАВИЛА:\n"
            f"1. Верни ТОЛЬКО чистый JSON без markdown-тегов.\n"
            f"2. Все строковые ключи и значения должны быть на русском языке.\n"
            f"3. Опирайся строго на факты из запроса, не выдумывай лишнего.\n"
        )

        raw_text = self.generate_text(prompt=prompt, system_prompt=strict_system, max_tokens=max_tokens, is_json=True)
        cleaned = self._clean_json_text(raw_text)

        try:
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except Exception as e:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return schema.model_validate(data)
                except Exception as e2:
                    pass
            raise ValueError(f"AI вернул некорректный формат JSON: {e}")

ai_service = AIService()
