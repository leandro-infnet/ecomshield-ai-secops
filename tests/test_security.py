import os
import asyncio
import re
from html.parser import HTMLParser
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import httpx
import pytest
from sqlmodel import Session, create_engine, select
from uvicorn import Config

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "synthetic-test-secret-with-at-least-32-characters"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["CORS_ORIGINS"] = "http://allowed.example"
os.environ.pop("BOOTSTRAP_USERNAME", None)
os.environ.pop("BOOTSTRAP_PASSWORD", None)

from app.api.routes import auth
from app.api.routes.auth import _attempts
from app.core.security import hash_password
from app.db import database
from app.db.models import Prediction, User
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
    try:
        yield APIClient()
    finally:
        _attempts.clear()
        engine.dispose()


def token(client, username, password):
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.parametrize("method,path", [
    ("POST", "/predict"), ("GET", "/predictions/1"),
], ids=["predict", "consulta"])
def test_protected_routes_require_token(client, method, path):
    kwargs = {"json": {"texto_cliente": "Onde esta meu pedido?"}} if method == "POST" else {}
    response = client.request(method, path, **kwargs)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("case", [
    "arbitrary", "expired", "tampered", "missing_exp", "missing_sub",
    "empty_sub", "unknown_user", "wrong_algorithm",
])
@pytest.mark.parametrize("method,path", [
    ("POST", "/predict"), ("GET", "/predictions/1"),
], ids=["predict", "consulta"])
def test_protected_routes_reject_invalid_token(client, case, method, path):
    claims = {"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    key = os.environ["SECRET_KEY"]
    algorithm = "HS256"
    if case == "expired":
        claims["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    elif case == "tampered":
        key = "another-synthetic-secret-with-at-least-64-characters-for-hmac-testing"
    elif case == "missing_exp":
        claims.pop("exp")
    elif case == "missing_sub":
        claims.pop("sub")
    elif case == "empty_sub":
        claims["sub"] = ""
    elif case == "unknown_user":
        claims["sub"] = "nobody"
    elif case == "wrong_algorithm":
        algorithm = "HS384"
    bearer = "arbitrary" if case == "arbitrary" else jwt.encode(claims, key, algorithm=algorithm)
    kwargs = {"json": {"texto_cliente": "Onde esta meu pedido?"}} if method == "POST" else {}
    response = client.request(method, path, headers={"Authorization": f"Bearer {bearer}"}, **kwargs)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    with Session(database.engine) as session:
        assert session.exec(select(Prediction)).all() == []


def test_valid_login_creates_prediction_for_authenticated_owner(client):
    alice = token(client, "alice", "alice-synthetic-password")
    response = client.post("/predict", json={"texto_cliente": "Onde esta meu pedido?"},
                           headers={"Authorization": f"Bearer {alice}"})
    assert response.status_code == 200
    assert set(response.json()) == {"id", "intencao_prevista", "confianca"}
    with Session(database.engine) as session:
        prediction = session.get(Prediction, response.json()["id"])
        assert prediction is not None
        owner = session.exec(select(User).where(User.username == "alice")).one()
        assert prediction.owner_id == owner.id
        assert prediction.texto_cliente == "Onde esta meu pedido?"


@pytest.mark.parametrize("username,password", [
    ("alice", "wrong-password"), ("nobody", "wrong-password"),
], ids=["senha_incorreta", "usuario_inexistente"])
def test_login_rejects_invalid_credentials(client, username, password):
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciais inválidas"}
    assert "access_token" not in response.json()


def test_prediction_ownership(client):
    alice = token(client, "alice", "alice-synthetic-password")
    bob = token(client, "bob", "bob-synthetic-password")
    records = []
    for bearer, message in [(alice, "Preciso de ajuda"), (bob, "Quero cancelar meu pedido")]:
        created = client.post("/predict", json={"texto_cliente": message},
                              headers={"Authorization": f"Bearer {bearer}"})
        assert created.status_code == 200
        records.append(created.json())
    assert records[0]["id"] != records[1]["id"]
    for owner, other, record in [(alice, bob, records[0]), (bob, alice, records[1])]:
        path = f"/predictions/{record['id']}"
        own = client.get(path, headers={"Authorization": f"Bearer {owner}"})
        denied = client.get(path, headers={"Authorization": f"Bearer {other}"})
        assert own.status_code == 200
        assert own.json() == record
        assert denied.status_code == 404
        assert denied.json() == {"detail": "Predição não encontrada"}


@pytest.mark.parametrize("body,error_type", [
    ({"texto_cliente": "Preciso de ajuda", "admin": True}, "extra_forbidden"),
    ({"texto_cliente": "Preciso de ajuda", "owner_id": 2}, "extra_forbidden"),
    ({}, "missing"),
    ({"texto_cliente": None}, "string_type"),
    ({"texto_cliente": 123}, "string_type"),
    ({"texto_cliente": "abcd"}, "string_too_short"),
    ({"texto_cliente": "x" * 101}, "string_too_long"),
], ids=["extra_admin", "extra_owner", "ausente", "nulo", "numero", "curto", "longo"])
def test_invalid_input_is_rejected_without_persisting(client, body, error_type):
    alice = token(client, "alice", "alice-synthetic-password")
    response = client.post("/predict", json=body, headers={"Authorization": f"Bearer {alice}"})
    assert response.status_code == 422
    assert any(error["type"] == error_type for error in response.json()["detail"])
    with Session(database.engine) as session:
        assert session.exec(select(Prediction)).all() == []


@pytest.mark.parametrize("length", [5, 100], ids=["minimo", "maximo"])
def test_input_length_boundaries_are_accepted(client, length):
    alice = token(client, "alice", "alice-synthetic-password")
    response = client.post("/predict", json={"texto_cliente": "x" * length},
                           headers={"Authorization": f"Bearer {alice}"})
    assert response.status_code == 200
    with Session(database.engine) as session:
        stored = session.get(Prediction, response.json()["id"])
        assert stored is not None
        assert stored.texto_cliente == "x" * length


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


def test_security_headers_and_cors(client):
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
    docs = client.get("/docs")
    assert "https://cdn.jsdelivr.net" in docs.headers["content-security-policy"]


def test_openapi_documents_authentication_and_ownership_errors(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    expected = {"/health": "get", "/auth/token": "post", "/predict": "post", "/predictions/{prediction_id}": "get"}
    assert set(paths) == set(expected)
    for path, method in expected.items():
        operation = paths[path][method]
        assert operation["description"]
        assert "$ref" in operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert "application/x-www-form-urlencoded" in paths["/auth/token"]["post"]["requestBody"]["content"]
    assert "application/json" in paths["/predict"]["post"]["requestBody"]["content"]
    for path, method in [("/predict", "post"), ("/predictions/{prediction_id}", "get")]:
        assert paths[path][method]["security"] == [{"OAuth2PasswordBearer": []}]
    assert paths["/auth/token"]["post"]["responses"]["429"]["headers"]["Retry-After"]
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "servico": "E-ComShield API operacional"}
    assert {"401", "429"} <= paths["/auth/token"]["post"]["responses"].keys()
    assert "401" in paths["/predict"]["post"]["responses"]
    assert {"401", "404"} <= paths["/predictions/{prediction_id}"]["get"]["responses"].keys()


def test_rate_limit_blocks_and_recovers_after_window(client, monkeypatch):
    # Substitui somente o relógio do módulo auth, sem alterar asyncio/time global.
    now = [1000.0]
    monkeypatch.setattr(auth, "time", SimpleNamespace(monotonic=lambda: now[0]))
    form = {"username": "alice", "password": "wrong-password"}
    for _ in range(5):
        assert client.post("/auth/token", data=form).status_code == 401
    valid = {"username": "alice", "password": "alice-synthetic-password"}
    blocked = client.post("/auth/token", data=valid)
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
    assert blocked.headers["x-frame-options"] == "DENY"
    assert blocked.headers["cross-origin-resource-policy"] == "same-origin"
    now[0] += 59
    assert client.post("/auth/token", data=valid).status_code == 429
    now[0] += 1
    assert client.post("/auth/token", data=valid).status_code == 200


def test_rate_limit_isolated_by_connection_ip(client):
    form = {"username": "nobody", "password": "wrong-password"}
    for _ in range(5):
        assert client.post("/auth/token", data=form).status_code == 401
    assert client.post("/auth/token", data=form).status_code == 429
    other_ip = APIClient(client_address=("203.0.113.50", 12345))
    assert other_ip.post("/auth/token", data=form).status_code == 401


@pytest.mark.parametrize("path", ["/docs", "/redoc"], ids=["swagger", "redoc"])
def test_documentation_uses_matching_nonce_and_asset_integrity(client, path):
    response = client.get(path)
    assert response.status_code == 200
    policy = response.headers["content-security-policy"]
    assert "unsafe-inline" not in policy
    assert "base-uri 'none'" in policy
    assert "form-action 'self'" in policy
    nonce = re.search(r"script-src 'nonce-([^']+)'", policy)
    assert nonce is not None
    tags = []

    class Tags(HTMLParser):
        def handle_starttag(self, tag, attrs):
            tags.append((tag, dict(attrs)))

    Tags().feed(response.text)
    scripts = [attrs for tag, attrs in tags if tag == "script"]
    assert scripts
    assert all(attrs.get("nonce") == nonce[1] for attrs in scripts)
    external = [attrs for attrs in scripts if "src" in attrs]
    external += [attrs for tag, attrs in tags if tag == "link" and attrs.get("rel") == "stylesheet"]
    assert external
    for attrs in external:
        assert attrs["integrity"].startswith("sha384-")
        assert attrs["crossorigin"] == "anonymous"
        assert re.search(r"@\d+\.\d+\.\d+/", attrs.get("src", attrs.get("href", "")))
    another_policy = client.get(path).headers["content-security-policy"]
    assert nonce[1] not in another_policy
    assert response.headers["cache-control"] == "no-store"
