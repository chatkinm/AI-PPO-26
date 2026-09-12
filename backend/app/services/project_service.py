import json
from pathlib import Path
from typing import List, Optional
from backend.app.models.project import Project
from backend.app.config import settings

PROJECTS_DB_FILE = settings.storage_dir / "projects.json"

class ProjectService:
    """Управление проектами ППО и сохранение состояний"""

    def _load_all(self) -> List[Project]:
        if not PROJECTS_DB_FILE.exists():
            return []
        try:
            with open(PROJECTS_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Project.model_validate(item) for item in data]
        except Exception:
            return []

    def _save_all(self, projects: List[Project]):
        PROJECTS_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROJECTS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump([p.model_dump() for p in projects], f, ensure_ascii=False, indent=2)

    def list_projects(self) -> List[Project]:
        return self._load_all()

    def get_project(self, project_id: str) -> Optional[Project]:
        projects = self._load_all()
        for p in projects:
            if p.id == project_id:
                return p
        return None

    def create_project(self, name: str) -> Project:
        import uuid
        project = Project(id=str(uuid.uuid4())[:8], name=name)
        projects = self._load_all()
        projects.insert(0, project)
        self._save_all(projects)
        return project

    def update_project(self, project: Project) -> Project:
        projects = self._load_all()
        for idx, p in enumerate(projects):
            if p.id == project.id:
                projects[idx] = project
                self._save_all(projects)
                return project
        projects.append(project)
        self._save_all(projects)
        return project

project_service = ProjectService()
