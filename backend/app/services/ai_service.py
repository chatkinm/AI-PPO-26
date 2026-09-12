import json
import re
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import groq
from backend.app.config import settings

logger = logging.getLogger("ai_service")
T = TypeVar("T", bound=BaseModel)

class AIService:
    def __init__(self):
        self.groq_client = groq.Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096, is_json: bool = False) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if self.groq_client:
            models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
            for model_name in models_to_try:
                try:
                    kwargs = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.2
                    }
                    if "qwen" in model_name:
                        kwargs["max_tokens"] = 950
                    else:
                        kwargs["max_tokens"] = max_tokens

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

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None, max_tokens: int = 4096) -> T:
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
