from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-style Document AI API for extracting structured data from PDFs/images using OCR + LLM/VLM pipelines.",
)

app.include_router(router)
