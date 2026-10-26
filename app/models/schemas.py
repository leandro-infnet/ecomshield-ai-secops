from pydantic import BaseModel, ConfigDict, Field


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
