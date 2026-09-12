from pydantic import BaseModel, Field
from typing import List, Optional

class RequirementItem(BaseModel):
    id: str = Field(description="ID требования, например REQ-01")
    category: str = Field(description="Категория: Функциональное, Интеграция, Безопасность, Бизнес")
    text: str = Field(description="Четкая формулировка требования")
    source: str = Field(description="Источник: Созвон от ДД.ММ, Смета, Прототип")
    status: str = Field(default="confirmed", description="confirmed / needs_review")

class Inconsistency(BaseModel):
    id: str = Field(description="ID противоречия, например INC-01")
    topic: str = Field(description="Тема противоречия")
    source_a: str = Field(description="Утверждение в источнике А")
    source_b: str = Field(description="Противоречащее утверждение в источнике Б")
    conflict_explanation: str = Field(description="В чем именно состоит конфликт или нестыковка")
    clarifying_question: str = Field(description="Сформулированный профессиональный вопрос для клиента")
    severity: str = Field(default="critical", description="critical (блокирует разработку) / minor (косметика)")
    status: str = Field(default="open", description="open / resolved / client_question_sent")

class AnalysisReport(BaseModel):
    confirmed_requirements: List[RequirementItem] = Field(default_factory=list)
    inconsistencies: List[Inconsistency] = Field(default_factory=list)
    missing_critical_topics: List[str] = Field(default_factory=list, description="Пробелы по онтологии Xpage")
    readiness_score: int = Field(default=0, description="Индекс готовности требований (0-100%)")
