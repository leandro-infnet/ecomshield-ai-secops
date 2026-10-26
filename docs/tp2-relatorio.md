# E-ComShield — relatório de entrega do TP2

## 1. Problema e objetivo

O TP2 aprofunda a análise do dataset de suporte ao cliente e fortalece a API FastAPI que registra predições demonstrativas. O objetivo futuro é classificar a intenção de mensagens; nesta etapa, **não há modelo treinado**. O retorno de `/predict` é um placeholder explícito, com confiança 0,0. Este documento é a fonte Markdown para a entrega; o PDF será produzido posteriormente pelo aluno.

## 2. Dados e análise exploratória

O [dataset Bitext](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) local tem 26.872 linhas, 27 intenções e 11 categorias. A [EDA executada](../notebooks/01_eda_ecomshield.ipynb) verificou tipos, ausentes, textos vazios, linhas duplicadas e repetições de `instruction`. Encontrou zero linhas inteiras duplicadas, 2.237 textos repetidos e nenhum texto repetido com `intent` conflitante. O bruto foi preservado.

O notebook contém histograma, barras de intenção, boxplot, heatmap Seaborn de correlação e scatter plot de caracteres versus palavras em amostra com semente fixa. A correlação entre caracteres e palavras foi $r=0{,}813$; isso descreve características do texto, sem comprovar valor preditivo para intenção. A [interpretação completa e limitações](eda/tp2.md) estão no relatório separado exigido pela tarefa 7.

### Teste da hipótese do TP1

A hipótese era que mensagens de `complaint` e `contact_customer_service` tendem a ser mais curtas. O [teste Mann–Whitney U](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html) unilateral (`alternative='less'`) comparou 2.000 mensagens dessas classes com 24.872 das demais, sob $\alpha=0{,}05$. Obteve $U=28.909.189{,}5$, $p=1{,}0$ arredondado, mediana 52 versus 48 caracteres. Não há suporte à direção proposta; as medianas apontam para a direção oposta. Templates repetidos e seleção da hipótese após a exploração limitam inferência populacional.

## 3. API e segurança

A API agora usa SQLModel e SQLite local. Um usuário inicial é criado a partir de variáveis de ambiente; sua senha é armazenada com PBKDF2-HMAC-SHA256 e salt aleatório. JWT exige segredo configurado, assinatura HS256 válida, expiração e sujeito existente. `POST /predict` aceita somente o campo textual permitido por Pydantic `extra='forbid'`, registra o placeholder e retorna ID. `GET /predictions/{id}` consulta simultaneamente o ID e `owner_id` obtido da identidade validada, devolvendo 404 ao outro usuário. As consultas são geradas por SQLModel, sem SQL raw.

O middleware adiciona HSTS, `X-Frame-Options`, `X-Content-Type-Options`, CSP, `Cache-Control: no-store` e outros headers descritos no [README](../README.md). CORS usa allowlist explícita. A autenticação limita cinco tentativas por IP de conexão em 60 segundos e retorna 429 com `Retry-After` na sexta. Esse limite reduz tentativas rápidas em uma instância; não cobre múltiplos processos nem substitui controles de rede. A [matriz OWASP API Top 10](security/owasp-api-top10.md), o [DFD](architecture/dfd.md) e a [análise STRIDE](security/stride.md) separam controles presentes de lacunas.

## 4. Evidências de validação

A suíte `venv/bin/python -m pytest tests/ -q` terminou com **5 testes aprovados**. Os cenários cobrem token ausente, arbitrário, expirado e adulterado; acesso ao recurso pelo dono e por outro usuário; body com campo extra, ausente, nulo, tipo incorreto e comprimentos inválidos; headers, CORS, 429 e documentação OpenAPI dos erros. Os testes usam SQLite temporário e identidades sintéticas. O notebook foi executado em kernel limpo na ordem das células, com outputs e gráficos gravados.

O [scan ZAP OpenAPI em modo seguro](security/zap-api-report.html) importou oito URLs e registrou `FAIL-NEW: 0` e `WARN-NEW: 0`. O [baseline complementar](security/zap-report.html) observou cinco URLs e registrou um warning informativo sobre `no-store`. Nos JSON finais não há finding de severidade Medium ou High. O [documento de findings](security/zap-findings.md) lista cada observação, correções feitas e o alcance real da auditoria. Como as rotas protegidas responderam 401 sem autenticação, o scan passivo não validou BOLA; esse cenário foi exercitado no pytest.

## 5. Limitações e próximos passos

A API usa SQLite e rate limiting em memória; não possui migrações, revogação de token, recuperação de conta, TLS próprio ou classificador treinado. O limite de 100 caracteres é demonstrativo e pode rejeitar mensagens legítimas. O dataset bruto é ignorado pelo Git e precisa ser obtido da fonte indicada para reproduzir a EDA. No TP3, separar textos repetidos antes de treinar e avaliar um baseline por classe; antes de uso real, definir infraestrutura de TLS, segredo, backups, quotas compartilhadas e auditoria autenticada.

## 6. Fontes e uso de IA

- [Dataset Bitext](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset).
- [SciPy: `mannwhitneyu`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html).
- [OWASP API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10/).
- [SQLModel: filtros `where`](https://sqlmodel.tiangolo.com/tutorial/where/).
- [OWASP ZAP: baseline](https://www.zaproxy.org/docs/docker/baseline-scan/) e [API scan em modo seguro](https://www.zaproxy.org/docs/docker/api-scan/).
- Codex (OpenAI) auxiliou na implementação, testes, execução da EDA, auditoria e redação. Os resultados numéricos e operacionais citados foram obtidos localmente; a análise e a entrega final foram revisadas por aluno (Leandro Medeiros).
