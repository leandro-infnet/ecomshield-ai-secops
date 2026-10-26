from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    username: str
    password: str
    grant_type: Literal["password"] | None = None
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    texto_cliente: str = Field(min_length=5, max_length=100, description="Mensagem do cliente")


class Token(BaseModel):
    access_token: str
    token_type: str


class PredictResponse(BaseModel):
    id: int
    intencao_prevista: str
    confianca: float
