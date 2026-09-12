from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import shutil
from backend.app.models.project import Project
from backend.app.services.project_service import project_service
from backend.app.config import settings

router = APIRouter(prefix="/api/projects", tags=["Projects"])

class CreateProjectRequest(BaseModel):
    name: str

@router.get("", response_model=List[Project])
async def list_projects():
    return project_service.list_projects()

@router.post("", response_model=Project)
async def create_project(req: CreateProjectRequest):
    return project_service.create_project(name=req.name)

@router.post("/load-demo", response_model=Project)
async def load_demo_project():
    """Создает предзаполненный демонстрационный проект на базе сквозного кейса Xpage"""
    project = project_service.create_project(name="Сквозной кейс: Приложение ломбарда (Xpage)")

    proj_dir = settings.uploads_dir / project.id
    proj_dir.mkdir(parents=True, exist_ok=True)

    # 1. Копируем эталонную смету
    source_est = settings.base_dir / "Примеры смет" / "GIGASCHOOL - смета на разработку мобильного приложения - .xlsx"
    if source_est.exists():
        target_est = proj_dir / source_est.name
        shutil.copyfile(source_est, target_est)
        project.estimate_file = str(target_est)

    # 2. Копируем транскрипты созвонов
    trans_folder = settings.base_dir / "Транскрибация созвонов с клиентом"
    if trans_folder.exists():
        for fname in ["19.06.2026_обезличено_обсуждение_технических_требований.docx", "21.04.2026_обезличено_технический_брифинг_и_интеграции.docx"]:
            src_t = trans_folder / fname
            if src_t.exists():
                dst_t = proj_dir / fname
                shutil.copyfile(src_t, dst_t)
                project.transcript_files.append(str(dst_t))

    project_service.update_project(project)
    return project

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    p = project_service.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return p
