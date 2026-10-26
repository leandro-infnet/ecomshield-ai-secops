import os
import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone

import jwt
import httpx
import pytest
from sqlmodel import Session, create_engine
from uvicorn import Config

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "synthetic-test-secret-with-at-least-32-characters"
os.environ["CORS_ORIGINS"] = "http://allowed.example"
os.environ.pop("BOOTSTRAP_USERNAME", None)
os.environ.pop("BOOTSTRAP_PASSWORD", None)

from app.api.routes.auth import _attempts
from app.core.security import hash_password
from app.db import database
from app.db.models import User
from app.main import app


class APIClient:
    def __init__(
        self,
        asgi_app: Callable[..., Awaitable[None]] = app,
        client_address: tuple[str, int] = ("127.0.0.1", 12345),
    ):
        self.asgi_app = asgi_app
        self.client_address = client_address

    def request(self, method, path, **kwargs):
        async def send():
            transport = httpx.ASGITransport(app=self.asgi_app, client=self.client_address)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, path, **kwargs)
        return asyncio.run(send())

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(database, "engine", engine)
    _attempts.clear()
    database.init_db()
    with Session(engine) as session:
        session.add(User(username="alice", password_hash=hash_password("alice-synthetic-password")))
        session.add(User(username="bob", password_hash=hash_password("bob-synthetic-password")))
        session.commit()
    yield APIClient()
    engine.dispose()


def token(client, username, password):
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_predict_requires_valid_token(client):
    body = {"texto_cliente": "Onde esta meu pedido?"}
    assert client.post("/predict", json=body).status_code == 401
    assert client.post("/predict", json=body, headers={"Authorization": "Bearer arbitrary"}).status_code == 401
    valid = token(client, "alice", "alice-synthetic-password")
    assert client.post("/predict", json=body, headers={"Authorization": f"Bearer {valid}"}).status_code == 200
    expired = jwt.encode({"sub": "alice", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}, os.environ["SECRET_KEY"], algorithm="HS256")
    assert client.post("/predict", json=body, headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    tampered = jwt.encode({"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}, "another-synthetic-secret-with-32-characters", algorithm="HS256")
    assert client.post("/predict", json=body, headers={"Authorization": f"Bearer {tampered}"}).status_code == 401


def test_prediction_ownership(client):
    alice = token(client, "alice", "alice-synthetic-password")
    bob = token(client, "bob", "bob-synthetic-password")
    created = client.post("/predict", json={"texto_cliente": "Preciso de ajuda"}, headers={"Authorization": f"Bearer {alice}"})
    assert created.status_code == 200
    prediction_id = created.json()["id"]
    assert client.get(f"/predictions/{prediction_id}", headers={"Authorization": f"Bearer {alice}"}).status_code == 200
    assert client.get(f"/predictions/{prediction_id}", headers={"Authorization": f"Bearer {bob}"}).status_code == 404


def test_extra_field_is_rejected(client):
    alice = token(client, "alice", "alice-synthetic-password")
    headers = {"Authorization": f"Bearer {alice}"}
    response = client.post("/predict", json={"texto_cliente": "Preciso de ajuda", "admin": True}, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"
    for body in ({}, {"texto_cliente": None}, {"texto_cliente": 123}, {"texto_cliente": "curto"[:4]}, {"texto_cliente": "x" * 101}):
        assert client.post("/predict", json=body, headers=headers).status_code == 422


def test_login_accepts_oauth2_form_and_rejects_extra_fields(client):
    form = {
        "username": "alice", "password": "alice-synthetic-password",
        "grant_type": "password", "scope": "", "client_id": "", "client_secret": "",
    }
    assert client.post("/auth/token", data=form).status_code == 200
    extra = client.post("/auth/token", data={**form, "admin": "true"})
    assert extra.status_code == 422
    assert any(error["type"] == "extra_forbidden" for error in extra.json()["detail"])
    assert client.post("/auth/token", data={**form, "grant_type": "client_credentials"}).status_code == 422


def test_rate_limit_ignores_forwarded_headers_when_proxy_headers_are_disabled(client):
    # Mesma configuração do comando local --no-proxy-headers no README.
    config = Config(app, proxy_headers=False, lifespan="off", log_config=None)
    config.load()
    runtime_client = APIClient(asgi_app=config.loaded_app)
    statuses = []
    for attempt in range(6):
        response = runtime_client.post(
            "/auth/token", data={"username": "nobody", "password": "wrong"},
            headers={"X-Forwarded-For": f"203.0.113.{attempt + 1}"},
        )
        statuses.append(response.status_code)
    assert statuses == [401, 401, 401, 401, 401, 429]


def test_headers_cors_and_rate_limit(client):
    response = client.get("/health")
    assert response.headers["strict-transport-security"].startswith("max-age=")
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"
    allowed = client.get("/health", headers={"Origin": "http://allowed.example"})
    denied = client.get("/health", headers={"Origin": "http://denied.example"})
    assert allowed.headers["access-control-allow-origin"] == "http://allowed.example"
    assert "access-control-allow-origin" not in denied.headers
    for _ in range(5):
        assert client.post("/auth/token", data={"username": "nobody", "password": "wrong"}).status_code == 401
    limited = client.post("/auth/token", data={"username": "nobody", "password": "wrong"})
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) > 0
    assert limited.headers["x-frame-options"] == "DENY"
    assert limited.headers["cross-origin-resource-policy"] == "same-origin"
    docs = client.get("/docs")
    assert "https://cdn.jsdelivr.net" in docs.headers["content-security-policy"]


def test_openapi_documents_authentication_and_ownership_errors(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert {"401", "429"} <= paths["/auth/token"]["post"]["responses"].keys()
    assert "401" in paths["/predict"]["post"]["responses"]
    assert {"401", "404"} <= paths["/predictions/{prediction_id}"]["get"]["responses"].keys()
