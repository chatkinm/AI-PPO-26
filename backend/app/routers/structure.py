from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil
from backend.app.models.structure import ProjectStructure
from backend.app.services.project_service import project_service
from backend.app.services.estimate_parser import estimate_parser
from backend.app.services.ai_service import ai_service
from backend.app.prompts.structure_prompts import STRUCTURE_SYSTEM_PROMPT, get_structure_prompt
from backend.app.config import settings

router = APIRouter(prefix="/api/structure", tags=["Structure"])

@router.post("/upload-estimate/{project_id}")
async def upload_estimate(project_id: str, file: UploadFile = File(...)):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Сохраняем файл
    proj_dir = settings.uploads_dir / project_id
    proj_dir.mkdir(parents=True, exist_ok=True)
    file_path = proj_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Парсим смету
    parsed = estimate_parser.parse_file(file_path)
    project.estimate_file = str(file_path)
    project_service.update_project(project)

    return {
        "status": "success",
        "filename": file.filename,
        "sheet_name": parsed["sheet_name"],
        "total_rows": parsed["total_rows"],
        "rows": parsed["rows"]
    }

@router.post("/generate/{project_id}", response_model=ProjectStructure)
async def generate_structure(project_id: str):
    project = project_service.get_project(project_id)
    if not project or not project.estimate_file:
        raise HTTPException(status_code=400, detail="Сначала загрузите смету проекта")

    parsed = estimate_parser.parse_file(Path(project.estimate_file))
    summary_lines = []
    for r in parsed["rows"]:
        elem_str = f" (элементы: {', '.join(r['elements'])})" if r['elements'] else ""
        summary_lines.append(f"Строка {r['row_index']} [{r['section']}]: {r['title']}{elem_str}")

    estimate_summary = "\n".join(summary_lines)
    prompt = get_structure_prompt(project.name, estimate_summary)

    structure = ai_service.generate_structured(
        prompt=prompt,
        schema=ProjectStructure,
        system_prompt=STRUCTURE_SYSTEM_PROMPT
    )

    project.structure = structure
    project.current_step = 2
    project_service.update_project(project)

    return structure

@router.put("/update/{project_id}", response_model=ProjectStructure)
async def update_structure(project_id: str, structure: ProjectStructure):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    project.structure = structure
    project_service.update_project(project)
    return structure
