"""Interfaces OpenAPI com CSP por resposta e assets fixados por SRI."""

import re
import secrets

from fastapi import APIRouter
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

router = APIRouter(include_in_schema=False)

ASSETS = {
    "swagger-ui-bundle.js": {
        "url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.34.1/swagger-ui-bundle.js",
        "integrity": "sha384-XFYN47VzPiDY6qPtxYKg0nqUeW/upo20xf1j2SUE7gT/i35FJB4cuS/71Iegzk8Z"
    },
    "swagger-ui.css": {
        "url": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.34.1/swagger-ui.css",
        "integrity": "sha384-4c3vsE5f+trhFyHrFrLM1fFGUn531NIaC7dcqEWIJdoRQJ5CkJbSuSCwXLpaS1KF"
    },
    "bundles/redoc.standalone.js": {
        "url": "https://cdn.jsdelivr.net/npm/redoc@2.5.4/bundles/redoc.standalone.js",
        "integrity": "sha384-w447zOpYfw/1Tv/5AK9NfHTlQIqE3RVR6KY62jCyy9zNDgO64cMwGGP1Fj0zJVf5"
    }
}


def documentation_response(kind: str) -> HTMLResponse:
    nonce = secrets.token_urlsafe(24)
    if kind == "swagger":
        response = get_swagger_ui_html(
            openapi_url="/openapi.json", title="E-ComShield API - Swagger UI",
            swagger_js_url=ASSETS["swagger-ui-bundle.js"]["url"],
            swagger_css_url=ASSETS["swagger-ui.css"]["url"],
            swagger_favicon_url="data:,",
        )
    else:
        response = get_redoc_html(
            openapi_url="/openapi.json", title="E-ComShield API - ReDoc",
            redoc_js_url=ASSETS["bundles/redoc.standalone.js"]["url"],
            redoc_favicon_url="data:,", with_google_fonts=False,
        )
    html = bytes(response.body).decode("utf-8")
    if kind == "redoc":
        # Inicialização explícita: getAttribute("nonce") pode ocultar o valor no DOM.
        html = html.replace('<redoc spec-url="/openapi.json"></redoc>', '<div id="redoc"></div>')
        html = html.replace("</body>", f'<script>Redoc.init("/openapi.json", {{nonce: "{nonce}"}}, document.getElementById("redoc"));</script></body>')
    html = re.sub(r"<(script|style)(?=[ >])", lambda match: f'<{match[1]} nonce="{nonce}"', html)
    for asset in ASSETS.values():
        for attribute in ("src", "href"):
            html = html.replace(f'{attribute}="{asset["url"]}"',
                                f'{attribute}="{asset["url"]}" integrity="{asset["integrity"]}" crossorigin="anonymous"')
    # CSS inicial do bundle ReDoc 2.5.4, antes da opção nonce ser aplicada.
    redoc_styles = (
        " 'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='"
        " 'sha256-QMIg+bpjm3JdElJ388KYke01izlUW0UoNOeKjpMxdgc='"
    ) if kind == "redoc" else ""
    image_sources = "'self' data: https://cdn.redoc.ly" if kind == "redoc" else "'self' data:"
    policy = (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}' https://cdn.jsdelivr.net; "
        f"style-src 'nonce-{nonce}' https://cdn.jsdelivr.net{redoc_styles}; "
        f"img-src {image_sources}; font-src 'self'; connect-src 'self'; "
        "worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    return HTMLResponse(html, headers={"Content-Security-Policy": policy})


@router.get("/docs")
def swagger_docs():
    return documentation_response("swagger")


@router.get("/redoc")
def redoc_docs():
    return documentation_response("redoc")
