from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import AuthenticatedUser, get_current_user
from app.db.database import get_session
from app.db.models import Prediction
from app.models.schemas import PredictRequest, PredictResponse

router = APIRouter()


@router.post(
    "/predict", response_model=PredictResponse, summary="Registra predição demonstrativa",
    responses={401: {"description": "Token ausente ou inválido"}},
)
def predict_intent(request: PredictRequest, user: AuthenticatedUser = Depends(get_current_user), session: Session = Depends(get_session)):
    prediction = Prediction(owner_id=user.id, texto_cliente=request.texto_cliente,
                            intencao_prevista="track_refund_placeholder", confianca=0.0)
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction


@router.get(
    "/predictions/{prediction_id}", response_model=PredictResponse, summary="Consulta predição própria",
    responses={401: {"description": "Token ausente ou inválido"}, 404: {"description": "Predição não encontrada"}},
)
def get_prediction(prediction_id: int, user: AuthenticatedUser = Depends(get_current_user), session: Session = Depends(get_session)):
    prediction = session.exec(select(Prediction).where(Prediction.id == prediction_id, Prediction.owner_id == user.id)).first()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Predição não encontrada")
    return prediction
