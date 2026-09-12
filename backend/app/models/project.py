from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.app.models.structure import ProjectStructure
from backend.app.models.analysis import AnalysisReport

class Project(BaseModel):
    id: str = Field(description="Уникальный идентификатор проекта")
    name: str = Field(description="Название проекта")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    current_step: int = Field(default=1, description="Текущий шаг визарда (1-4)")
    estimate_file: Optional[str] = None
    transcript_files: List[str] = Field(default_factory=list)
    figjam_url: Optional[str] = None
    structure: Optional[ProjectStructure] = None
    analysis: Optional[AnalysisReport] = None
    tz_path: Optional[str] = None
