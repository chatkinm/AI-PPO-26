import httpx
from typing import Dict, Any, List, Optional
from backend.app.config import settings

class FigmaService:
    """Сервис интеграции с Figma / FigJam REST API"""

    def __init__(self):
        self.token = settings.figma_access_token

    def _extract_file_key(self, url_or_key: str) -> str:
        """Извлекает ключ файла из ссылки Figma/FigJam вида https://www.figma.com/board/ABC123xyz/..."""
        if "/" not in url_or_key:
            return url_or_key
        parts = url_or_key.split("/")
        for idx, p in enumerate(parts):
            if p in ["board", "file", "design"] and idx + 1 < len(parts):
                return parts[idx + 1].split("?")[0]
        return url_or_key

    async def get_file_content(self, url_or_key: str) -> Dict[str, Any]:
        file_key = self._extract_file_key(url_or_key)
        headers = {"X-Figma-Token": self.token}
        url = f"https://api.figma.com/v1/files/{file_key}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise ValueError(f"Figma API error {resp.status_code}: {resp.text[:200]}")
            return resp.json()

    def parse_figjam_nodes(self, figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Фильтрует только смысловые ноды FigJam (стикеры, блоки, секции)"""
        document = figma_data.get("document", {})
        extracted_nodes = []

        def traverse(node):
            node_type = node.get("type")
            name = node.get("name", "").strip()
            text = node.get("characters", "").strip()

            if node_type in ["STICKY", "SHAPE_WITH_TEXT", "SECTION", "FRAME"]:
                extracted_nodes.append({
                    "id": node.get("id"),
                    "type": node_type,
                    "name": name,
                    "text": text or name
                })

            for child in node.get("children", []):
                traverse(child)

        traverse(document)
        return extracted_nodes

figma_service = FigmaService()
