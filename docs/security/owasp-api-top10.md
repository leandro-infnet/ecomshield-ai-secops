# 🛡️ Controles frente ao OWASP API Security Top 10 (2023)

A [lista OWASP](https://api-security.owasp.org/editions/2023/en/0x11-t10/) organiza riscos comuns em APIs; sua presença neste mapa não equivale a conformidade integral. O escopo é a API local do TP2, ainda sem modelo real ou integrações externas.

| Risco | Controle atual | Lacuna ou condição |
| --- | --- | --- |
| API1 — Broken Object Level Authorization | `GET /predictions/{id}` consulta `id` e `owner_id` autenticado; teste com outro usuário recebe 404. | Nova rota por ID exigirá a mesma verificação. |
| API2 — Broken Authentication | JWT HS256 com assinatura, expiração e usuário existente; senha PBKDF2 com salt; 429 após cinco tentativas/minuto/IP. O comando local desabilita proxy headers para impedir contorno por `X-Forwarded-For` forjado. | Sem recuperação de conta, revogação de token ou rate limit distribuído. |
| API3 — Broken Object Property Level Authorization | `LoginRequest` e `PredictRequest` proíbem extras; a resposta de predição expõe apenas `id`, intenção e confiança. | Não há rotas de atualização de propriedades. |
| API4 — Unrestricted Resource Consumption | 100 caracteres por mensagem e rate limit no login. | Sem limites globais, de conexão, de concorrência ou do banco; estes devem ser configurados na infraestrutura. |
| API5 — Broken Function Level Authorization | Não há ações administrativas expostas. | Funções futuras precisarão de escopos/papéis. |
| API6 — Unrestricted Access to Sensitive Business Flows | Placeholder não executa estornos nem outras transações. | Fluxos transacionais futuros precisarão de controles próprios. |
| API7 — Server Side Request Forgery | Nenhuma URL do cliente é usada em chamadas externas. | Reavaliar quando houver ferramentas ou integrações. |
| API8 — Security Misconfiguration | Segredo obrigatório, CORS explícito, headers HSTS, X-Frame-Options, nosniff, CSP, CORP e no-store. | TLS, proteção de banco e gestão de segredos dependem do ambiente. |
| API9 — Improper Inventory Management | OpenAPI documenta rotas locais; `/health` não expõe detalhes internos. | Sem inventário automatizado de versões/implantações. |
| API10 — Unsafe Consumption of APIs | Nenhuma API externa é chamada em runtime. | A origem e integridade de dados externos devem ser revistas antes de treinamento. |

Os [testes](../../tests/test_security.py) verificam os controles centrais. O [relatório ZAP](zap-findings.md) apresenta apenas os achados passivos observados nas rotas alcançadas. Nem testes locais nem scan passivo demonstram a ausência de todas as classes de vulnerabilidade.
