from pydantic import BaseModel, Field
from typing import List, Optional

class ScreenElement(BaseModel):
    name: str = Field(description="Название элемента или блока")
    type: str = Field(default="generic", description="Тип: button, input, list, banner, card, modal, etc.")
    description: Optional[str] = Field(default="", description="Описание назначения или поведения")

class Screen(BaseModel):
    id: str = Field(description="Уникальный ID экрана (e.g. SCR-01)")
    title: str = Field(description="Название экрана")
    purpose: str = Field(default="", description="Назначение экрана")
    elements: List[ScreenElement] = Field(default_factory=list, description="Список элементов интерфейса")
    source_row: Optional[int] = Field(default=None, description="Строка из сметы")
    requires_clarification: bool = Field(default=False, description="Требует ли логика экрана уточнения")

class Module(BaseModel):
    id: str = Field(description="Уникальный ID модуля")
    name: str = Field(description="Название раздела / модуля")
    description: Optional[str] = Field(default="", description="Описание функциональной группы")
    screens: List[Screen] = Field(default_factory=list, description="Экраны модуля")

class ProjectStructure(BaseModel):
    project_name: str = Field(description="Название проекта")
    modules: List[Module] = Field(default_factory=list, description="Список модулей системы")
