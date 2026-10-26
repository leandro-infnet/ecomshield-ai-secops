from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Verifica a integridade da API")
async def health_check():
    return {"status": "ok", "servico": "E-ComShield API operacional"}
