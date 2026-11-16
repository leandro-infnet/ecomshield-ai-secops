# 🛡️ TP3 — Auditoria final e prontidão da API

**Exercício 4 concluído no ambiente local sintético.** A API iniciou com seu lifespan real, respondeu aos fluxos de autenticação e autorização e disponibilizou OpenAPI e interfaces renderizadas. Após corrigir os findings das páginas de documentação, o reteste ZAP registrou **zero High, Medium ou Low** e somente três tipos de alerta informativo. A suíte final teve **39 testes aprovados**.

A prontidão aqui é técnica e local. A exposição para outra equipe depende de endereço acessível, autorização, janela e limites acordados no planejamento T2; não houve pentest de terceiros, scan ativo ou publicação da API.

## 1. Escopo e evidências

Execução local em **09/11/2026, UTC−03**, registrada também em UTC nos artefatos. Alvo: `http://127.0.0.1:18081`, com SQLite exclusivo em diretório temporário, contas `alice` e `bob` e mensagens sintéticas. O proxy ZAP foi vinculado a `127.0.0.1:18082`, em modo **safe**, com análise passiva limitada ao contexto desse alvo. Não foram usados `.env`, banco operacional ou dataset.

| Evidência | Artefato |
| --- | --- |
| Auditoria inicial | [JSON ZAP](tp3/zap-inicial.json), [HTML ZAP](tp3/zap-inicial.html) e [checks HTTP iniciais](tp3/runtime-inicial.json) |
| Reteste após as correções | [JSON ZAP final](tp3/zap-report.json), [HTML ZAP final](tp3/zap-report.html) e [checks HTTP finais](tp3/runtime.json) |
| Contrato de todos os endpoints | [OpenAPI exportado](tp3/openapi.json) |
| Suíte de segurança final | [Saída sanitizada do pytest: 39 passed in 6.92s](tp3/pytest.txt) |
| Swagger no navegador | [Captura](tp3/swagger.png) e [verificações do navegador](tp3/swagger-browser.json) |
| ReDoc no navegador | [Captura](tp3/redoc.png) e [verificações do navegador](tp3/redoc-browser.json) |
| Versões, imagem e hashes dos assets | [Ferramentas](tp3/ferramentas.json) |

Foram observadas **23 requisições HTTP controladas**, incluindo respostas 200, 401, 404, 422 e 429. As requisições passaram pelo proxy; não houve spider, fuzzing ou active scan. Os alertas do ZAP complementam as verificações específicas de BOLA e autenticação, sem substituí-las.

Ferramentas: ZAP **2.17.0**, imagem identificada por digest no artefato, Chromium **156.0.8078.79**, Python **3.14.4** e pytest **9.1.1**. Senhas, chave e JWTs foram removidos dos relatórios, e o whitespace foi normalizado sem alterar os dados dos JSONs; os arquivos de sessão e credenciais permanecem fora do repositório. A fila passiva chegou a zero antes da exportação final.

## 2. Findings, correções e reteste

Os relatórios do [TP2](zap-findings.md) não tinham Medium/High, mas não cobriam as interfaces de documentação. O tráfego desta auditoria revelou novas configurações a corrigir. A severidade abaixo vem de `riskcode` no JSON; confiança alta em um alerta informativo não o torna High.

| ID ZAP | Finding inicial e endpoints | Severidade | Risco e tratamento | Verificação e status |
| --- | --- | --- | --- | --- |
| 10055-13 | CSP: Failure to Define Directive with No Fallback, `/redoc` | Medium | Diretiva sem fallback não restringida explicitamente; acrescentadas `base-uri` e `form-action` | Ausente no relatório final; **resolvido** |
| 10055-5 | CSP: script-src unsafe-inline, `/docs` e `/redoc` | Medium | Permissão ampla para scripts inline; substituída por nonce aleatório por resposta | Ausente no reteste; navegador e pytest verificaram o contrato; **resolvido** |
| 10055-6 | CSP: style-src unsafe-inline, `/docs` e `/redoc` | Medium | Permissão ampla para estilos inline; substituída por nonce e hashes específicos do CSS inicial do ReDoc fixado | Ausente no reteste, interfaces renderizadas sem erros de CSP; **resolvido** |
| 90003 | Sub Resource Integrity Attribute Missing, `/docs` e `/redoc` | Medium | Assets externos sem verificação de conteúdo; versões exatas e hashes SHA-384 adicionados a JS/CSS com `crossorigin=anonymous`; Google Fonts removido | Ausente no reteste e assets carregados no navegador; **resolvido** |
| 10017 | Cross-Domain JavaScript Source File Inclusion, `/docs` e `/redoc` | Low | JavaScript de terceiro; URLs fixadas e protegidas por SRI, com CSP específica | Alerta ausente no final; dependência da CDN permanece documentada; **resolvido no escopo auditado** |
| 10109 | Modern Web Application, `/docs` e `/redoc` | Informational | Identifica interfaces JavaScript esperadas | Presente, **aceito**; não é indicação de exploração |
| 10111 | Authentication Request Identified, `/auth/token` | Informational | Identifica o formulário de autenticação esperado | Presente, **aceito**; relatório sanitizado |
| 10112 | Session Management Response Identified, `/auth/token` | Informational | Identifica emissão de token esperada | Presente, **aceito**; tokens removidos da evidência |

O relatório inicial agrupou quatro tipos Medium e um Low; o final contém três tipos informativos, com cinco instâncias agrupadas. Não há Medium/High aceito como exceção ou pendente. Nenhuma regra foi desativada para ocultar os achados.

Além dos findings ZAP, o navegador identificou o favicon externo bloqueado pela política original. As interfaces agora usam favicon `data:`. O ReDoc permite a origem específica de seu logo em `img-src`; seus estilos gerados recebem nonce por inicialização explícita. Os dois hashes adicionais de estilo são restritos ao conteúdo inicial do bundle ReDoc **2.5.4**, incluindo o estilo vazio: devem ser revistos se o bundle mudar.

## 3. OpenAPI e funcionamento das interfaces

`/health` passou a declarar `HealthResponse`. Os erros 401, 404 e 429 pertinentes passaram a declarar `ErrorResponse`, e o 429 documenta `Retry-After`. Os quatro endpoints têm descrições e schemas de saída; as duas operações de entrada documentam formulário ou JSON, conforme o contrato real. As rotas protegidas declaram o esquema OAuth2 Bearer.

As descrições deixam explícitos o placeholder, o armazenamento do texto, o limite de entrada e a autorização por proprietário. Não foi treinado ou integrado um classificador. As interfaces `/docs` e `/redoc` usam rotas próprias, fora do schema, mantendo os endereços existentes e a especificação em `/openapi.json`.

O Chromium carregou as quatro operações e os schemas do Swagger, abriu o diálogo de autenticação e executou **GET /health pelo Try it out**, recebendo 200. O ReDoc renderizou as operações e modelos. Não foram observados erros de CSP nas versões finais. O Swagger emitiu somente uma recomendação DOM sobre seu campo de senha fora de um formulário, registrada no JSON; ela não foi tratada como finding de segurança ZAP. A abertura do diálogo não comprova login pelo navegador: o login e os JWTs foram verificados pelas requisições HTTP e pytest.

Os assets continuam externos à aplicação, fixados em Swagger UI **5.34.1** e ReDoc **2.5.4**. A renderização requer acesso à CDN; mudança de versão exige recalcular SRI, revisar a CSP e repetir a inspeção. `/docs/oauth2-redirect` não é exposto pelas rotas próprias: o fluxo usado é OAuth2 password, sem redirecionamento de authorization code.

## 4. Checklist de prontidão

| Controle / cenário | Status | Evidência e limite |
| --- | --- | --- |
| Inicialização e encerramento pelo Uvicorn/lifespan | Resolvido | Instância TCP local iniciou sem erro crítico; `/health` respondeu 200. Health não verifica serviços externos |
| Autenticação e token expirado | Resolvido | Login das duas contas 200; rota sem token e com JWT expirado 401; suíte cobre adulteração, claims e algoritmo |
| Autorização por proprietário — BOLA | Resolvido | Donos consultam seus registros com 200; acesso cruzado retorna 404 nos dois sentidos |
| Campos desconhecidos e entradas inválidas | Resolvido | HTTP 422 e verificação de ausência de persistência pela suíte |
| Limite de login | Resolvido no processo local | Sexta tentativa na janela retorna 429 com Retry-After; recuperação e headers forjados exercitados por pytest |
| Headers e CORS | Resolvido no escopo verificado | Origem permitida liberada, origem não permitida sem header; CSP, cache e demais headers verificados |
| HSTS / TLS | Aceito como limite do ambiente | Header presente; HTTP local não fornece TLS nem proteção HSTS efetiva. A exposição externa exige configuração própria |
| OpenAPI e schemas | Resolvido | `/openapi.json` exportado; contratos conferidos por pytest |
| Swagger e ReDoc funcionais | Resolvido | Chromium com CSP efetiva, SRI e operações renderizadas; Try it out de health 200 |
| Findings Medium/High | Resolvido | Zero no relatório ZAP final, sem aceitação dessas severidades |
| Suíte final | Resolvido | 39 testes aprovados, incluindo dois casos adicionais de documentação |
| Contas e dados sintéticos | Resolvido localmente | Script cria duas contas, predições e banco isolado; credenciais fora do repositório |
| CI e proteção de main | Resolvido nas evidências do exercício 3 | [Checks obrigatórios, bloqueio e recuperação](../ci/index.md) comprovados com a suíte de 37 casos daquele momento; publicação desta alteração fará o workflow executar os 39 casos atuais |
| Alvo externo e acordo com equipe adversária | Planejado para exercício 6 | URL/IP acessível, autorização, endpoints, janela e limites ainda dependem de acordo; não autoriza ataques neste exercício |

**Decisão:** GO técnico para testes controlados nesta instância local; liberação entre equipes condicionada ao acordo e à acessibilidade do ambiente. Não se declara prontidão de produção, rate limiting distribuído, TLS implantado ou segurança completa pelo resultado passivo.

## 5. Reprodução e dados de teste

Da raiz, com as dependências do projeto instaladas, iniciar a instância em um terminal:

```bash
venv/bin/python -m scripts.ambiente_pentest --diretorio /tmp/ecomshield-pentest --porta 18081
```

O [script do ambiente](../../scripts/ambiente_pentest.py) ignora `.env`, força banco no diretório informado e escuta somente em loopback, com proxy headers desabilitados. Um diretório novo é recomendado. Se omitido, cria um diretório temporário e informa seu caminho. Um diretório não vazio sem configuração conhecida é rejeitado. Ao reutilizar um ambiente criado pelo script, preserva credenciais e dados sintéticos.

`ambiente.json` guarda chave e senhas sintéticas com permissão 0600; abra esse arquivo apenas localmente para fornecer as contas ao operador autorizado. Ele não deve ser incluído em commits ou anexos. Não altere as senhas no JSON de um banco já criado: o script não implementa rotação. Cada usuário recebe uma predição inicial; novas requisições podem criar outras.

Para repetir a análise passiva, usar **um ZAP dedicado e descartável**, em outro terminal:

```bash
docker run --rm --name ecomshield-tp3-zap --network host \
  ghcr.io/zaproxy/zaproxy@sha256:5ccfff9a411743ab2615136a2edd7416bec9ce41572fa94e935df38c14adb2b6 \
  zap.sh -daemon -host 127.0.0.1 -port 18082 \
  -config api.disablekey=true \
  -config autoupdate.checkOnStart=false \
  -config autoupdate.downloadNewRelease=false \
  -config autoupdate.installAddonUpdates=false
```

A API administrativa sem chave está restrita ao loopback nesta configuração de laboratório, sem publicação externa. O comando com rede host foi validado neste Linux/WSL; não se presume equivalência em todos os ambientes Docker Desktop.

Em um terceiro terminal, escolher uma pasta de saída nova ou vazia:

```bash
venv/bin/python -m scripts.auditoria_passiva \
  --ambiente /tmp/ecomshield-pentest \
  --saida /tmp/ecomshield-zap-reteste
```

O [script de auditoria](../../scripts/auditoria_passiva.py) usa apenas os endereços locais fixos acima, inicia uma sessão nova no ZAP dedicado, ativa modo safe e inclui somente o alvo no contexto passivo. Faz as 23 verificações, espera a fila terminar, exporta HTML/JSON e remove credenciais conhecidas e JWTs. A saída não deve sobrescrever os relatórios versionados sem comparação e revisão. Se repetir na mesma instância da API logo após atingir 429, reinicie a instância ou aguarde a janela real de 60 segundos antes do próximo ciclo.

Para inspeção visual, abrir `/docs` e `/redoc` no navegador, conferir o console, os schemas, o diálogo Authorize e o Try it out de `/health`. Para a suíte:

```bash
venv/bin/python -m pytest tests/ -v
```

O comando de reprodução foi conferido em uma nova pasta temporária: 23 checks aprovados e zero Medium/High, sem sobrescrever os relatórios vinculados. As instâncias usadas na auditoria foram encerradas ao final; para novos testes, reinicie pelo comando acima.

Encerrar a instância com Ctrl+C e o contêiner com `docker stop ecomshield-tp3-zap`. Acesso externo, brute force, carga/DoS e operações destrutivas não fazem parte desta reprodução. As contas possuem o mesmo papel; a diferença de proprietário permite testar BOLA. Papéis adicionais dependerão de requisitos futuros.

## Fontes e uso de IA

- [ZAP: análise passiva e API](https://www.zaproxy.org/docs/api/) e [modo seguro do API Scan](https://www.zaproxy.org/docs/docker/api-scan/). Esta auditoria utilizou proxy manual e API do ZAP, não o comando API Scan.
- [FastAPI: modelos de resposta](https://fastapi.tiangolo.com/tutorial/response-model/) e [customização das interfaces de documentação](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/).
- [W3C: Content Security Policy](https://www.w3.org/TR/CSP/latest) e bundles públicos identificados em [ferramentas.json](tp3/ferramentas.json).
- Codex (OpenAI) auxiliou na implementação, execução local do ZAP/HTTP/pytest, automação do Chromium e redação. Resultados vieram das execuções registradas; Leandro revisa decisões e limites. O agente não executou operações Git mutáveis, publicação ou mensagens a terceiros.

Continue pela [visão geral do projeto](../../README.md), pelo [glossário](../glossario.md) e pelo planejamento da classificação nos exercícios seguintes.
