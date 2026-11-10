import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, documentation, health, predict
from app.core.security import secret_key
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    secret_key()
    init_db()
    yield


app = FastAPI(title="E-ComShield API", description="API demonstrativa consolidada no TP3. Autenticação JWT, registro de predições placeholder e consulta por proprietário. Ainda não há classificador treinado. Use somente dados sintéticos nos testes.", version="2.0.0", lifespan=lifespan, docs_url=None, redoc_url=None)
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"], allow_credentials=False)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if "Content-Security-Policy" not in response.headers:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return response


app.include_router(health.router, tags=["Operacional"])
app.include_router(auth.router, tags=["Autenticação"])
app.include_router(predict.router, tags=["Predições"])

app.include_router(documentation.router)
