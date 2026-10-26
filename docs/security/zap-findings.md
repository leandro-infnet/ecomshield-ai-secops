# Auditoria passiva OWASP ZAP — TP2

## Escopo e execução

A auditoria usou a imagem oficial `ghcr.io/zaproxy/zaproxy:stable` contra a API iniciada **somente em `127.0.0.1:18081`**, com SQLite e conta sintéticos. O scan principal foi `zap-api-scan.py` com `-f openapi -S` (modo seguro: sem scan ativo) e importou oito URLs do `/openapi.json`. O baseline complementar usou `zap-baseline.py` com spider de um minuto; alcançou cinco URLs. O [guia oficial do baseline](https://www.zaproxy.org/docs/docker/baseline-scan/) descreve o spider seguido de análise passiva. Não houve tráfego a API externa nem teste de terceiros.

Relatórios exportados: [OpenAPI JSON](zap-api-report.json), [OpenAPI HTML](zap-api-report.html), [baseline JSON](zap-report.json) e [baseline HTML](zap-report.html). Os arquivos foram verificados quanto a senha sintética, `SECRET_KEY` e Bearer token antes de serem incluídos. O scan OpenAPI recebeu 200 em `/health` e `/openapi.json`; as rotas protegidas responderam 401 sem token. O baseline incluiu `/`, `/robots.txt` e `/sitemap.xml`, que responderam 404.

## Findings finais

No relatório ZAP, `riskdesc` apresenta **severidade antes dos parênteses** e confiança dentro deles. Por exemplo, `Informational (High)` significa severidade informativa com confiança alta; não é finding de severidade High.

| ID | Finding | Severidade / confiança | Onde | Interpretação e status |
| --- | --- | --- | --- | --- |
| 100000 | A Client Error response code was returned by the server | Informational / High | Três respostas 401 de rotas protegidas | Esperado sem token; **aceito** no escopo do scan não autenticado. |
| 10111 | Authentication Request Identified | Informational / Low | `/auth/token` | ZAP identificou o formulário de login; **informativo**, sem correção. |
| 10049 | Non-Storable Content | Informational / Medium | Respostas com `Cache-Control: no-store` | Consequência deliberada da política de não armazenar respostas; **aceito**. |

**Findings Medium ou High: nenhum** nos relatórios finais. Assim, não há finding dessas severidades a corrigir ou aceitar. O resumo do scan OpenAPI registrou `FAIL-NEW: 0` e `WARN-NEW: 0`; o baseline registrou `WARN-NEW: 1` para o item informativo 10049, pois trata observações da regra como warning. A severidade foi conferida no JSON exportado.

## Correções durante a auditoria

Na primeira execução, ZAP apontou `Storable and Cacheable Content` (Informational) e `Cross-Origin-Resource-Policy Header Missing or Invalid` (Low) nas respostas sem autenticação. Adicionamos `Cache-Control: no-store` e `Cross-Origin-Resource-Policy: same-origin` no middleware. Os relatórios vinculados acima são os scans **repetidos após a correção**; o alerta Low desapareceu, e o item de cache passou a `Non-Storable Content`, resultado esperado.

## Limitações e próximos passos

O scan foi passivo e não autenticado. Ele não exerceu respostas 200 de `/predict` ou `/predictions/{id}`, não testou BOLA, injeção SQL ou força bruta, e não demonstra ausência de vulnerabilidades. Esses controles foram verificados separadamente pela [suíte pytest](../../tests/test_security.py) com duas identidades e banco temporário. Antes de produção, repetir auditoria em ambiente autorizado com autenticação configurada, TLS, rate limiting compartilhado e observabilidade. Nenhuma ação de scan ativo foi executada neste TP2.
