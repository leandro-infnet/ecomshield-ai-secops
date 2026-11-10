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
    texto_cliente: str = Field(min_length=5, max_length=100, description="Mensagem do cliente; de 5 a 100 caracteres", examples=["Onde esta meu pedido?"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    servico: str


class ErrorResponse(BaseModel):
    detail: str = Field(description="Descrição do erro, sem credenciais ou tokens")


class Token(BaseModel):
    access_token: str = Field(description="JWT a enviar no header Authorization: Bearer <token>")
    token_type: str = Field(description="Tipo do token: bearer")


class PredictResponse(BaseModel):
    id: int
    intencao_prevista: str = Field(description="Placeholder demonstrativo; não é classificação por modelo treinado")
    confianca: float = Field(description="Valor demonstrativo 0.0; não é probabilidade calibrada")
