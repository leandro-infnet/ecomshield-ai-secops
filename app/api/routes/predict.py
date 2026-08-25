from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.schemas import PredictRequest, PredictResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/predict", response_model=PredictResponse, summary="Predição de intenção")
async def predict_intent(request: PredictRequest, token: str = Depends(oauth2_scheme)):
    # O Depends(oauth2_scheme) exige o token. Sem ele, o FastAPI retorna 401 automaticamente.
    return PredictResponse(
        intencao_prevista="track_refund_placeholder",
        confianca=0.95
    )
