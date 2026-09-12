import docx
from typing import List, Dict, Any
from pathlib import Path

class TranscriptParser:
    """Парсер DOCX транскрибаций созвонов с клиентом"""

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        doc = docx.Document(str(file_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        metadata = []
        dialogues = []
        current_speaker = "Неизвестный спикер"

        for p in paragraphs:
            # Метаданные встречи в первых строках
            if any(marker in p for marker in ["2026", "2025", "Проект:", "Обезличенная версия", "Часть "]):
                metadata.append(p)
                continue

            if p.startswith("Спикер ") or p.startswith("Спикер:"):
                current_speaker = p
                continue

            # Проверяем, есть ли тайм-код (например 00:01:23 - ...)
            dialogues.append({
                "speaker": current_speaker,
                "text": p
            })

        return {
            "filename": file_path.name,
            "metadata": "\n".join(metadata),
            "dialogue_count": len(dialogues),
            "full_text": "\n".join([f"{d['speaker']}: {d['text']}" for d in dialogues])
        }

transcript_parser = TranscriptParser()
