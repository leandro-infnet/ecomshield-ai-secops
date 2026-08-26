from pydantic import BaseModel, Field

class Token(BaseModel):
  access_token: str
  token_type: str

class PredictRequest(BaseModel):
  # Field delimita tamanho do input prevenindo Denial of Service
  # (DoS) por payloads excessivamente longos (Buffer Overflow).
  texto_cliente: str = Field(..., min_length=5, max_length=100, description="Mensagem do cliente")

class PredictResponse(BaseModel):
  intencao_prevista: str
  confianca: float
