# 🛡️ E-ComShield — TP2

API demonstrativa de atendimento para registrar uma intenção placeholder por mensagem e consultar o registro pelo proprietário. O projeto inclui EDA estatística e controles de segurança do TP2. **Ainda não há modelo treinado:** `track_refund_placeholder` e `confianca=0.0` não representam inferência nem probabilidade calibrada.

## 📚 Percurso de leitura

- [Relatório central do TP2 para futura exportação em PDF](docs/tp2-relatorio.md)
- [Relatório de EDA](docs/eda/tp2.md) e [notebook executado](notebooks/01_eda_ecomshield.ipynb)
- [Fluxo de dados](docs/architecture/dfd.md), [ameaças](docs/security/stride.md), [mapa OWASP API Top 10](docs/security/owasp-api-top10.md) e [findings ZAP](docs/security/zap-findings.md)
- [Glossário](docs/glossario.md) e [changelog](CHANGELOG.md)

## 🚀 Início rápido

Requer Python 3.12+; o ambiente verificado usa Python 3.14.4. As versões de NumPy e SciPy fixadas em `requirements.txt` exigem pelo menos Python 3.12. Para reproduzir a EDA, obtenha o dataset Bitext em `data/raw/bitext_intent.csv`. O dataset é ignorado pelo Git; consulte a [fonte oficial](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset). Da raiz do repositório:

```bash
python -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

Configure um `.env` local, ignorado pelo Git, com valores próprios. `SECRET_KEY` precisa ter pelo menos 32 caracteres. `BOOTSTRAP_USERNAME` e `BOOTSTRAP_PASSWORD` criam um usuário inicial somente se ele ainda não existir; alterar a senha depois exige procedimento de gestão de usuários ainda não implementado.

```env
SECRET_KEY=troque-por-uma-chave-aleatoria-com-ao-menos-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./data/processed/ecomshield.db
BOOTSTRAP_USERNAME=usuario_local
BOOTSTRAP_PASSWORD=senha-local-escolhida-pelo-operador
CORS_ORIGINS=http://127.0.0.1:3000
```

```bash
venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

`GET /health` deve retornar `status: ok`. `POST /auth/token` recebe formulário `username` e `password`, devolvendo JWT válido por 30 minutos por padrão. O formulário também aceita os campos de compatibilidade OAuth2 `grant_type` (quando informado, somente `password`), `scope`, `client_id` e `client_secret`; a autenticação usa usuário e senha, sem conceder escopos ou autenticar aplicações clientes. Campos desconhecidos retornam 422. `POST /predict` exige `Authorization: Bearer <token>` e JSON com `texto_cliente` de 5 a 100 caracteres; retorna um ID e o placeholder. `GET /predictions/{id}` retorna apenas registro do dono autenticado, ou 404. A documentação OpenAPI está em `/docs`.

## 🔒 Segurança e limites

A API valida assinatura HS256, expiração e sujeito do JWT contra usuário existente. Senhas são armazenadas com PBKDF2-HMAC-SHA256 e salt aleatório. A consulta de predição filtra `id` e `owner_id` com SQLModel; o dono vem da identidade validada. Os modelos de entrada de `/auth/token` e `/predict` usam Pydantic `extra='forbid'` e rejeitam campos extras com 422. `/predict` também rejeita tipos não textuais e entradas fora dos limites. Respostas incluem HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` e CSP. CORS aceita apenas as origens em `CORS_ORIGINS`; vazio significa nenhuma origem permitida ao navegador.

`/auth/token` aceita **cinco tentativas por IP de conexão a cada 60 segundos**; a sexta recebe 429 e `Retry-After`. A janela curta dificulta tentativas rápidas de senha em uma instância local sem impor bloqueio permanente. O comando local usa `--no-proxy-headers` para que o Uvicorn preserve o IP da conexão, mesmo quando o cliente envia `X-Forwarded-For`. Sem essa opção, o Uvicorn confia por padrão em headers enviados por clientes loopback, permitindo contornar o limite ao variar o IP declarado. Atrás de um proxy real, será necessário configurar explicitamente os proxies confiáveis e a sanitização desses headers. O contador é em memória por processo e não serve como controle distribuído em múltiplas réplicas; requer armazenamento compartilhado e controles de infraestrutura em produção. HSTS só tem efeito em HTTPS; o servidor local HTTP é demonstrativo. `/docs` e `/redoc` usam CSP específica para os assets da interface hospedados no jsDelivr, enquanto respostas da API usam política mais restritiva.

O SQLite local é demonstrativo. Não há migrações, recuperação de conta, rotação de chave, TLS na própria aplicação, monitoramento de abuso nem inferência real. Os textos enviados são armazenados no banco local; use apenas dados sintéticos em testes.

## ✅ Verificação

```bash
venv/bin/python -m pytest tests/
```

A suíte usa SQLite temporário, dados sintéticos e desabilita o carregamento de `.env`. Os sete testes incluem rejeição de extras no login e limite de tentativas com `X-Forwarded-For` variável na cadeia ASGI do Uvicorn configurada com proxy headers desabilitados. Veja o [relatório ZAP](docs/security/zap-findings.md) para escopo e achados do scan passivo. Um scan passivo não substitui testes autenticados de autorização nem comprova conformidade integral com o OWASP Top 10.

## Fontes e uso de IA

- [OWASP API Security Top 10 de 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)
- [SQLModel: consultas filtradas](https://sqlmodel.tiangolo.com/tutorial/where/)
- [OWASP ZAP: baseline passivo](https://www.zaproxy.org/docs/docker/baseline-scan/)
- Codex (OpenAI) auxiliou no código, análise, testes e redação do TP2; os resultados informados nos artefatos vieram de execuções locais.
