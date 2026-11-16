from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="Verifica a disponibilidade da API",
            description="Rota pública de disponibilidade do processo. Não verifica serviços externos ou modelo de ML.")
async def health_check():
    return {"status": "ok", "servico": "E-ComShield API operacional"}
