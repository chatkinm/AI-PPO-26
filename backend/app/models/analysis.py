from pydantic import BaseModel, Field
from typing import List, Optional

class ChecklistAuditItem(BaseModel):
    block_number: int = Field(description="Номер блока чек-листа (1-20)")
    block_name: str = Field(description="Название блока чек-листа")
    status: str = Field(
        default="gap", 
        description="confirmed (Согласовано) | contradiction (Противоречие) | gap (Белое пятно / Требует решения)"
    )
    risk_level: str = Field(
        default="high", 
        description="critical (🔴 Критическая) | high (🟡 Высокая) | medium (🔵 Средняя)"
    )
    points_evaluated: List[str] = Field(default_factory=list, description="Проверенные поинты из чек-листа")
    findings: str = Field(default="", description="Что выяснено из встреч и сметы по этому блоку")
    risk_description: str = Field(default="", description="Описание риска для проекта при отсутствии решения")
    recommendation_or_question: str = Field(default="", description="Рекомендация аналитика или вопрос Заказчику")

class RequirementItem(BaseModel):
    id: str = Field(description="ID требования, например REQ-01")
    category: str = Field(description="Категория: Функциональное, Интеграция, Безопасность, Бизнес")
    text: str = Field(description="Четкая формулировка требования")
    source: str = Field(description="Источник: Созвон от ДД.ММ, Смета, Прототип")
    status: str = Field(default="confirmed", description="confirmed / needs_review")

class Inconsistency(BaseModel):
    id: str = Field(description="ID противоречия, например INC-01")
    block_number: Optional[int] = Field(default=None, description="Номер связанного блока чек-листа (1-20)")
    topic: str = Field(description="Тема противоречия")
    source_a: str = Field(description="Утверждение в источнике А")
    source_b: str = Field(description="Противоречащее утверждение в источнике Б")
    conflict_explanation: str = Field(description="В чем именно состоит конфликт или нестыковка")
    clarifying_question: str = Field(description="Сформулированный профессиональный вопрос для клиента")
    severity: str = Field(default="critical", description="critical (🔴 Критическая) / high (🟡 Высокая) / minor (🔵 Средняя)")
    impact_area: Optional[str] = Field(default="", description="Зона влияния: Архитектура, Финансы/Смета, Сроки, ИБ, Юриспруденция")
    status: str = Field(default="open", description="open / resolved / client_question_sent")

class AnalysisReport(BaseModel):
    readiness_score: int = Field(default=0, description="Индекс готовности требований (0-100%)")
    checklist_audit: List[ChecklistAuditItem] = Field(
        default_factory=list, 
        description="Детальный аудит по 20 блокам эталонного чек-листа ППО Xpage"
    )
    inconsistencies: List[Inconsistency] = Field(
        default_factory=list, 
        description="Выявленные противоречия между встречами и сметой"
    )
    confirmed_requirements: List[RequirementItem] = Field(
        default_factory=list, 
        description="Согласованные технические и бизнес требования"
    )
    missing_critical_topics: List[str] = Field(
        default_factory=list, 
        description="Критические белые пятна (Gaps) по онтологии Xpage"
    )
