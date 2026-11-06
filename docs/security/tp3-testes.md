# 🔒 TP3 — Testes de segurança da API

O exercício 2 está coberto pela [suíte pytest](../../tests/test_security.py): **37 casos aprovados, em 13 funções de teste**, abrangendo autenticação, autorização por proprietário, validação de entradas e rate limiting. A [saída sanitizada da execução](tp3-pytest.txt) registra `37 passed in 6.97s`. Os casos parametrizados aparecem individualmente no resultado para facilitar o diagnóstico.

## Cenários e resultados esperados

| Controle | Teste em `tests/test_security.py` | Casos | Resultado verificado |
| --- | --- | ---: | --- |
| Autenticação obrigatória | `test_protected_routes_require_token` | 2 | POST e consulta protegidos retornam 401 sem token, com desafio Bearer |
| Validação do JWT | `test_protected_routes_reject_invalid_token` | 16 | Nas duas rotas, token arbitrário, expirado, assinado por outra chave, sem expiração, sem sujeito, com sujeito vazio/inexistente ou algoritmo diferente retorna 401; não cria predição |
| Caminho autorizado | `test_valid_login_creates_prediction_for_authenticated_owner` | 1 | Login válido permite registrar predição; banco associa o dono à identidade autenticada e a resposta mantém seu contrato |
| Credenciais inválidas | `test_login_rejects_invalid_credentials` | 2 | Senha incorreta e usuário inexistente retornam 401 com a mesma mensagem genérica, sem emitir token |
| BOLA | `test_prediction_ownership` | 1 | Duas contas criam recursos distintos; cada dono consulta o próprio registro (200), e a outra conta recebe 404, nos dois sentidos |
| Entradas inválidas | `test_invalid_input_is_rejected_without_persisting` | 7 | Extras `admin` e `owner_id`, texto ausente, nulo, numérico, curto ou longo retornam 422 com o tipo de erro esperado e sem registro no banco |
| Limites válidos | `test_input_length_boundaries_are_accepted` | 2 | Textos de 5 e 100 caracteres retornam 200 e são persistidos sem alteração |
| Formulário de login | `test_login_accepts_oauth2_form_and_rejects_extra_fields` | 1 | Formulário OAuth2 compatível funciona; campos desconhecidos e grant_type não permitido retornam 422 |
| Headers forjados | `test_rate_limit_ignores_forwarded_headers_when_proxy_headers_are_disabled` | 1 | Na cadeia ASGI do Uvicorn com proxy headers desabilitados, variar X-Forwarded-For não evita 429 na sexta tentativa |
| Headers e CORS | `test_security_headers_and_cors` | 1 | Resposta inclui headers previstos; só a origem permitida recebe liberação CORS; CSP específica está presente em /docs |
| Contrato OpenAPI | `test_openapi_documents_authentication_and_ownership_errors` | 1 | Respostas 401, 404 e 429 pertinentes estão declaradas no schema |
| Bloqueio e recuperação | `test_rate_limit_blocks_and_recovers_after_window` | 1 | Cinco falhas de login são permitidas; a sexta tentativa, mesmo com senha correta, recebe 429 e Retry-After; continua bloqueada aos 59 s e libera aos 60 s |
| Isolamento por IP | `test_rate_limit_isolated_by_connection_ip` | 1 | O bloqueio de um IP não impede a primeira tentativa de outro IP |

BOLA (Broken Object Level Authorization) é uma falha de autorização em que um usuário acessa um objeto de outro ao trocar seu identificador. A verificação usa recursos existentes e confirma também o acesso do dono, evitando confundir proteção com uma rota que nega tudo. Conceitos adicionais estão no [glossário](../glossario.md).

## Isolamento e reprodução

Da raiz, com as dependências instaladas no ambiente virtual:

```bash
venv/bin/python -m pytest tests/ -v
```

A suíte usa configuração sintética explícita antes da importação da aplicação, desabilita o carregamento de `.env` e remove configuração de bootstrap herdada. Cada caso recebe SQLite temporário e duas contas sintéticas; o engine é substituído na camada de banco. O contador de tentativas é limpo antes e depois dos casos, e o engine é liberado ao terminar. Nenhuma dependência de autenticação é substituída por usuário fictício: as requisições exercitam o login e a validação real do JWT.

A recuperação do limite usa um relógio controlado somente no módulo de autenticação, sem espera real nem alteração do relógio global de asyncio. Os demais testes usam o comportamento normal do relógio. O teste de headers de proxy usa a configuração `proxy_headers=False`, correspondente à execução local documentada no [README](../../README.md).

## Diagnóstico da execução anterior

A tentativa no sandbox permaneceu na primeira requisição, e o diagnóstico de timeout mostrou espera no event loop e no worker AnyIO. O mesmo teste, sem alterações, passou em 0,63 segundo fora do sandbox; a suíte ampliada passou nesse ambiente com Python 3.14.4 e pytest 9.1.1. A comparação indica impedimento do ambiente restrito; não identifica, por si só, a causa interna exata. O código da API não precisou ser alterado para os cenários exercitados.

## Limites da evidência e continuidade

Os testes enviam requisições HTTP à aplicação via transporte ASGI em processo, sem servidor TCP. O transporte atual não executa o lifespan; inicialização real, documentação renderizada no navegador, TLS e auditoria ZAP serão verificados no exercício 4. A aprovação não demonstra resistência a DoS, proteção distribuída do rate limiting, ausência de todas as vulnerabilidades nem cobertura estatística completa do código.

O [workflow do exercício 3](tp3-ci.md) integra a mesma suíte ao GitHub Actions. A [sequência de evidências remotas](../ci/index.md) demonstra a falha controlada dos testes de expiração, o bloqueio do merge e a recuperação após restaurar a validação, complementando a execução local deste exercício.

## Fontes e uso de IA

- [Implementação exercitada](../../app/main.py), [autenticação](../../app/core/security.py), [limite de tentativas](../../app/api/routes/auth.py) e [autorização por proprietário](../../app/api/routes/predict.py).
- Codex (OpenAI) auxiliou no diagnóstico, ampliação dos testes e redação do exercício 2. A evidência vinculada veio de execução local real, com caminhos da máquina substituídos por marcadores; não contém senhas ou tokens.
