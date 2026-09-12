import groq
from pathlib import Path
from backend.app.config import settings

class WhisperService:
    """Сервис транскрибации аудиофайлов через Groq Whisper API"""

    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def transcribe_audio(self, audio_path: Path) -> str:
        if not self.client:
            raise ValueError("GROQ_API_KEY не сконфигурирован в .env")

        with open(str(audio_path), "rb") as f:
            transcription = self.client.audio.transcriptions.create(
                file=(audio_path.name, f.read()),
                model=settings.groq_whisper_model,
                response_format="verbose_json",
                language="ru",
                temperature=0.0
            )
        return transcription.text

whisper_service = WhisperService()
