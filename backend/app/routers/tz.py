from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from backend.app.services.project_service import project_service
from backend.app.services.tz_generator import tz_generator
from backend.app.config import settings

router = APIRouter(prefix="/api/tz", tags=["Technical Specification"])

@router.post("/generate/{project_id}")
async def generate_tz(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    out_dir = settings.output_dir / project_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"ТЗ_{project.name}.docx"

    tz_data = {
        "modules": [m.model_dump() for m in project.structure.modules] if project.structure else []
    }

    generated_path = tz_generator.generate_docx(
        project_name=project.name,
        tz_data=tz_data,
        output_path=out_file,
        project=project
    )

    project.tz_path = str(generated_path)
    project.current_step = 4
    project_service.update_project(project)

    return {
        "status": "success",
        "file_name": generated_path.name,
        "download_url": f"/api/tz/download/{project_id}"
    }

@router.get("/download/{project_id}")
async def download_tz(project_id: str):
    project = project_service.get_project(project_id)
    if not project or not project.tz_path or not Path(project.tz_path).exists():
        raise HTTPException(status_code=404, detail="Файл ТЗ еще не сгенерирован")

    return FileResponse(
        path=project.tz_path,
        filename=Path(project.tz_path).name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
