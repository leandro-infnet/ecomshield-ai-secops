import threading
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlmodel import Session, select

from app.core.security import create_access_token, verify_password
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import ErrorResponse, LoginRequest, Token

router = APIRouter()
_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = threading.Lock()
LIMIT = 5
WINDOW_SECONDS = 60


def check_rate_limit(request: Request):
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _lock:
        attempts = _attempts[client]
        while attempts and attempts[0] <= now - WINDOW_SECONDS:
            attempts.popleft()
        if len(attempts) >= LIMIT:
            retry_after = max(1, int(WINDOW_SECONDS - (now - attempts[0])) + 1)
            raise HTTPException(status_code=429, detail="Limite de tentativas excedido", headers={"Retry-After": str(retry_after)})
        attempts.append(now)


@router.post(
    "/auth/token", response_model=Token, summary="Gera token JWT",
    description="Recebe formulário OAuth2 de usuário e senha. Cinco tentativas por IP de conexão em 60 segundos; a sexta retorna 429. Não concede escopos ou autentica aplicações clientes.",
    dependencies=[Depends(check_rate_limit)],
    responses={401: {"description": "Credenciais inválidas", "model": ErrorResponse},
               429: {"description": "Limite de tentativas excedido", "model": ErrorResponse,
                     "headers": {"Retry-After": {"description": "Segundos até nova tentativa", "schema": {"type": "integer"}}}}},
)
def login_for_access_token(
    form_data: Annotated[LoginRequest, Form()],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(user.username), token_type="bearer")
