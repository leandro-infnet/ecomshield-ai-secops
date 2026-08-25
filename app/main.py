from fastapi import FastAPI
from app.api.routes import health, auth, predict

app = FastAPI(
    title="E-ComShield API",
    description="API preditiva com autenticação JWT (TP1)",
    version="1.0.0"
)

# Registra os roteadores isolados
app.include_router(health.router, tags=["Operacional"])
app.include_router(auth.router, tags=["Autenticação"])
app.include_router(predict.router, tags=["IA / Agente"])
