from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.app.services.project_service import project_service
from backend.app.services.figma_service import figma_service
from backend.app.services.figjam_layout import generate_pawnshop_architecture, generate_dynamic_vertical_architecture

router = APIRouter(prefix="/api/figjam", tags=["FigJam"])

class FigJamSyncRequest(BaseModel):
    url_or_key: str

@router.get("/projects")
async def list_figjam_projects():
    """Возвращает список проектов со структурой для выбора в плагине FigJam"""
    all_projects = project_service.list_projects()
    result = []
    for p in all_projects:
        has_struct = p.structure is not None and len(p.structure.modules) > 0
        mod_count = len(p.structure.modules) if has_struct else 0
        scr_count = sum(len(m.screens) for m in p.structure.modules) if has_struct else 0
        result.append({
            "id": p.id,
            "name": p.name,
            "has_structure": has_struct,
            "modules_count": mod_count,
            "screens_count": scr_count,
            "created_at": p.created_at
        })
    return result

@router.get("/nodes/{project_id}")
async def get_figjam_nodes(project_id: str):
    """
    Рассчитывает корпоративное дерево экранов и коннекторов с координатами (x, y) 
    по стандарту Xpage для нативного программного создания на холсте FigJam без ручных действий.
    """
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    proj_name = (project.name or "").lower()
    is_pawnshop = "ломбард" in proj_name or "pawnshop" in proj_name or (
        project.structure and "ломбард" in (project.structure.project_name or "").lower()
    )

    if is_pawnshop:
        data = generate_pawnshop_architecture()
    else:
        if not project.structure or not project.structure.modules:
            raise HTTPException(status_code=400, detail="У проекта еще нет сформированной структуры")
        data = generate_dynamic_vertical_architecture(project)

    data["project_id"] = project.id
    data["project_name"] = project.name
    return data

@router.post("/sync/{project_id}")
async def sync_figjam(project_id: str, req: FigJamSyncRequest):
    """
    Чтение данных существующего прототипа Figma/FigJam через REST API
    для обогащения структуры и итогового ТЗ (требование кейса Xpage).
    """
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    try:
        raw_data = await figma_service.get_file_content(req.url_or_key)
        nodes = figma_service.parse_figjam_nodes(raw_data)
        
        project.figjam_url = req.url_or_key
        project_service.update_project(project)

        return {
            "status": "success",
            "file_name": raw_data.get("name"),
            "editor_type": raw_data.get("editorType", "figjam"),
            "extracted_nodes_count": len(nodes),
            "nodes": nodes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения Figma/FigJam: {str(e)}")

