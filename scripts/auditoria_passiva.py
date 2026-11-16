"""Analisa passivamente uma instância sintética local através de um ZAP dedicado."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time

import httpx
import jwt

BASE = "http://127.0.0.1:18081"
ZAP = "http://127.0.0.1:18082"
HEALTH_PATH = "/health"
AUTH_TOKEN_PATH = "/auth/token"
PREDICT_PATH = "/predict"


def call_zap(api, path, **params):
    response = api.get(path, params=params)
    response.raise_for_status()
    data = response.json()
    if "code" in data:
        raise RuntimeError(str(data))
    return data


def wait_for_zap(api):
    for _ in range(30):
        try:
            return call_zap(api, "/JSON/core/view/version/")["version"]
        except httpx.HTTPError:
            time.sleep(1)
    raise RuntimeError("ZAP não iniciou.")


def configure_zap_context(api):
    # O ZAP deve ser exclusivo deste laboratório: a sessão anterior é substituída.
    call_zap(api, "/JSON/core/action/newSession/", name="", overwrite="true")
    call_zap(api, "/JSON/core/action/setMode/", mode="safe")
    call_zap(api, "/JSON/context/action/newContext/", contextName="TP3")
    call_zap(api, "/JSON/context/action/includeInContext/", contextName="TP3", regex=f"{re.escape(BASE)}/.*")
    call_zap(api, "/JSON/pscan/action/setScanOnlyInScope/", onlyInScope="true")


def run_http_checks(output, private, sensitive_values):
    records = []
    rejected_input = "invalid-synthetic"
    with httpx.Client(base_url=BASE, proxy=ZAP, timeout=30, trust_env=False) as client:
        def request(method, path, expected, **kwargs):
            response = client.request(method, path, **kwargs)
            records.append({"metodo": method, "rota": path, "esperado": expected, "obtido": response.status_code})
            assert response.status_code == expected, (method, path, response.status_code)
            return response

        request("GET", HEALTH_PATH, 200)
        request("GET", "/docs", 200)
        request("GET", "/redoc", 200)
        schema = request("GET", "/openapi.json", 200).json()
        (output / "openapi.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n")
        tokens = {}
        for name, password in private["usuarios"].items():
            tokens[name] = request("POST", AUTH_TOKEN_PATH, 200, data={"username": name, "password": password}).json()["access_token"]
            sensitive_values.append(tokens[name])
        headers = {name: {"Authorization": f"Bearer {token}"} for name, token in tokens.items()}
        created = {}
        for name in tokens:
            created[name] = request("POST", PREDICT_PATH, 200, headers=headers[name], json={"texto_cliente": "Mensagem sintetica para auditoria"}).json()["id"]
        for owner, other in [("alice", "bob"), ("bob", "alice")]:
            path = f"/predictions/{created[owner]}"
            request("GET", path, 200, headers=headers[owner])
            request("GET", path, 404, headers=headers[other])
        request("POST", PREDICT_PATH, 401, json={"texto_cliente": "Mensagem sintetica sem token"})
        request("GET", f'/predictions/{created["alice"]}', 401)
        expired = jwt.encode({"sub": "alice", "exp": 1}, private["secret_key"], algorithm="HS256")
        sensitive_values.append(expired)
        request("POST", PREDICT_PATH, 401, json={"texto_cliente": "Mensagem sintetica expirada"}, headers={"Authorization": f"Bearer {expired}"})
        request("POST", PREDICT_PATH, 422, json={"texto_cliente": "Mensagem sintetica com extra", "admin": True}, headers=headers["alice"])
        request("POST", PREDICT_PATH, 422, json={"texto_cliente": None}, headers=headers["alice"])
        request("POST", AUTH_TOKEN_PATH, 422, data={"username": "alice", "password": rejected_input, "admin": "true"})
        for _ in range(2):
            request("POST", AUTH_TOKEN_PATH, 401, data={"username": "nobody", "password": rejected_input})
        limited = request("POST", AUTH_TOKEN_PATH, 429, data={"username": "nobody", "password": rejected_input})
        assert int(limited.headers["retry-after"]) > 0
        allowed = request("GET", HEALTH_PATH, 200, headers={"Origin": "http://127.0.0.1:3000"})
        denied = request("GET", HEALTH_PATH, 200, headers={"Origin": "https://denied.invalid"})
        assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
        assert "access-control-allow-origin" not in denied.headers
    return records, created


def wait_for_passive_scan(api):
    time.sleep(2)
    for _ in range(60):
        pending = int(call_zap(api, "/JSON/pscan/view/recordsToScan/")["recordsToScan"])
        if pending == 0:
            return pending
        time.sleep(1)
    raise RuntimeError("Fila passiva não terminou.")


def redact_sensitive_text(text, sensitive_values):
    for value in sorted(sensitive_values, key=len, reverse=True):
        text = text.replace(value, "[REDACTED]")
    return re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*", "[REDACTED_JWT]", text)


def export_zap_reports(api, output, sensitive_values):
    for name, path in [("zap-report.json", "/OTHER/core/other/jsonreport/"), ("zap-report.html", "/OTHER/core/other/htmlreport/")]:
        response = api.get(path)
        response.raise_for_status()
        sanitized = redact_sensitive_text(response.text, sensitive_values)
        assert not any(value in sanitized for value in sensitive_values)
        if name.endswith(".json"):
            sanitized = json.dumps(json.loads(sanitized), ensure_ascii=False, indent=2) + "\n"
        else:
            sanitized = "\n".join(line.rstrip() for line in sanitized.splitlines()) + "\n"
        (output / name).write_text(sanitized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ambiente", type=Path, required=True, help="Diretório gerado por scripts.ambiente_pentest")
    parser.add_argument("--saida", type=Path, required=True, help="Diretório novo ou vazio para relatórios sanitizados")
    args = parser.parse_args()
    output = args.saida
    if output.exists() and any(output.iterdir()):
        parser.error("Use uma saída vazia para preservar evidências anteriores.")
    output.mkdir(parents=True, exist_ok=True)
    private = json.loads((args.ambiente / "ambiente.json").read_text())
    sensitive_values = [private["secret_key"], *private["usuarios"].values()]

    with httpx.Client(base_url=ZAP, timeout=30, trust_env=False) as api:
        version = wait_for_zap(api)
        configure_zap_context(api)
        records, created = run_http_checks(output, private, sensitive_values)
        pending = wait_for_passive_scan(api)
        alerts = call_zap(api, "/JSON/core/view/alerts/", baseurl=BASE)["alerts"]
        export_zap_reports(api, output, sensitive_values)
        summary = {
            "alvo": BASE, "zap": version, "modo": call_zap(api, "/JSON/core/view/mode/")["mode"],
            "fila_passiva": pending, "instante_utc": datetime.now(timezone.utc).isoformat(),
            "requisicoes": records, "ids_criados": created,
            "alertas": [{"id": alert["pluginId"], "alerta": alert["alert"], "risco": alert["risk"], "url": alert["url"]} for alert in alerts],
        }
        (output / "runtime.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        blocking = [alert for alert in alerts if alert["risk"] in {"Medium", "High"}]
        print(f"HTTP checks: {len(records)}; ZAP {version}; modo {summary['modo']}; Medium/High: {len(blocking)}")
        if blocking:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
