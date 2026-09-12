from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.routers import projects, structure, analysis, figjam, tz

app = FastAPI(
    title="Xpage PPO AI Assistant API",
    description="Внутренний AI-сервис компании Xpage для автоматизации предпроектного обследования",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi import Request, Response

@app.middleware("http")
async def add_universal_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# Подключение роутеров API
app.include_router(projects.router)
app.include_router(structure.router)
app.include_router(analysis.router)
app.include_router(figjam.router)
app.include_router(tz.router)

# Статика и веб-интерфейс
frontend_dir = settings.base_dir / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(str(frontend_dir / "index.html"))

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "service": "Xpage PPO AI Assistant",
        "keys_configured": {
            "google_ai": bool(settings.google_api_key),
            "groq": bool(settings.groq_api_key),
            "figma": bool(settings.figma_access_token)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.backend_host, port=settings.backend_port, reload=settings.debug)
