# 📝 Changelog

## 📊 Ainda não publicado — TP3

- Exercício 3: workflow de segurança em push e pull request, Python 3.14 e job `security-tests`; instalação e testes verificados em ambiente limpo, com orientações para proteger `main`. Execução e bloqueio de merge remotos ainda pendentes.

- Exercício 2: suíte de segurança ampliada para 37 casos, com autenticação nas duas rotas protegidas, BOLA nos dois sentidos, validação sem persistência indevida e recuperação do rate limiting; matriz de cobertura e evidência sanitizada da execução.

- Exercício 1: notebook de regressão simples e múltipla com divisão por grupos de textos, baseline da média, R², RMSE, residual plots e Q-Q plots.
- Resultados reproduzíveis em JSON, figura exportada e discussão das limitações da regressão para classificar intenções.
- Dependências de scikit-learn adicionadas sem atualização das dependências anteriores.

## 📦 Ainda não publicado — TP2

- API com validação JWT, armazenamento SQLModel, consulta de predição por proprietário, cabeçalhos HTTP, CORS e limite de tentativas de login.
- Testes de segurança com banco temporário e dados sintéticos.
- EDA executada com duplicatas, correlações, dispersão e teste Mann–Whitney; relatório separado.
- Auditoria ZAP passiva em modo seguro e análise de findings em `docs/security/`.
- Consultas e hash de senha executados fora do event loop; respostas 401, 404 e 429 documentadas no OpenAPI.
- Formulário de autenticação com rejeição de campos extras e compatibilidade OAuth2; regressão para headers de proxy forjados com `--no-proxy-headers` na execução local.
- Pré-requisito ajustado para Python 3.12+ e descrição dos testes separada da inspeção das consultas SQLModel.
