import sys
import socket
from pathlib import Path

# 1. Добавляем корень проекта в sys.path
ROOT_DIR = Path(__file__).resolve().parent
if ROOT_DIR.name == "backend":
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from backend.app.config import settings

def get_free_port(host, preferred_port):
    for port in [preferred_port, 8080, 8008, 8050, 5000]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
            s.close()
            return port
        except OSError:
            continue
    return preferred_port

if __name__ == "__main__":
    port = get_free_port(settings.backend_host, settings.backend_port)
    print("=" * 65)
    print("Xpage AI-сервис предпроектного обследования (ППО)")
    print(f"Веб-интерфейс: http://{settings.backend_host}:{port}")
    print(f"Документация Swagger: http://{settings.backend_host}:{port}/docs")
    print("=" * 65)
    uvicorn.run(
        "backend.app.main:app",
        host=settings.backend_host,
        port=port,
        reload=settings.debug
    )
