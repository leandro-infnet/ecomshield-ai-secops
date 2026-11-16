# 📋 Consolidação do TP3

Os exercícios 1 a 5 possuem artefatos de implementação e evidência. O exercício 6
possui planejamento técnico concluído, mas **permanece parcial por falta de colega
adversário, URL/IP e confirmação de acesso**. Essa pendência impede declarar o TP3
integralmente concluído. A matriz abaixo orienta a revisão; não substitui a avaliação
do professor.

## Entregas e rubrica

| Item | Requisito resumido | Artefato e evidência | Situação |
| --- | --- | --- | --- |
| 1 | Pré-processamento, regressão simples e múltipla | [Notebook executado](../notebooks/02_regressao_ecomshield.ipynb) e [relatório](eda/tp3-regressao.md) | Evidência disponível |
| 2 | R² e RMSE calculados e interpretados | [Resultados e discussão](eda/tp3-regressao.md), com [JSON](eda/tp3-regressao-resultados.json) | Evidência disponível |
| 3 | Limites da regressão para classificar intenções | [Limitações da regressão](eda/tp3-regressao.md) e [pergunta de classificação](classificacao-tp3.md) | Documentado |
| 4 | Pelo menos cinco casos de autenticação, BOLA, entradas e rate limiting | [Suíte](../tests/test_security.py) e [matriz de cobertura](security/tp3-testes.md) | Evidência disponível |
| 5 | Workflow automático no GitHub Actions | [Workflow](../.github/workflows/security-tests.yml), [configuração](security/tp3-ci.md) e [evidências remotas](ci/index.md) | Evidência disponível |
| 6 | Suíte aprovada | [Execução final registrada: 39 casos](security/tp3/pytest.txt) | Evidência local disponível |
| 7 | Classes e distribuição no dataset | [Documento de classificação](classificacao-tp3.md) e [27 classes em CSV](eda/tp3-distribuicao-intencoes.csv) | Documentado e calculado |
| 8 | Justificativa do aprendizado supervisionado | [Argumentos e limitações baseados nos dados](classificacao-tp3.md) | Documentado |
| 9 | Modelo, atributos e justificativa do plano T2 | [Planejamento técnico](planejamento-t2.md) | Planejado; sem treinamento |
| 10 | Colega adversário e URL/IP definidos | [Pendências do acordo](planejamento-t2.md#5-acordo-adversarial--pendência-obrigatória) | **Pendente** |
| 11 | Findings ZAP Medium/High resolvidos | [Auditoria inicial, correções e reteste](security/tp3-auditoria-final.md) | Evidência no ambiente local auditado |
| 12 | OpenAPI acessível e schemas dos endpoints | [Auditoria e verificação das interfaces](security/tp3-auditoria-final.md) e [especificação salva](security/tp3/openapi.json) | Evidência no ambiente local auditado |

## Alcance das evidências

A regressão estima comprimento de texto; seus resultados não representam acurácia
de classificação. O corpus contém 26.872 exemplos em inglês e 27 intenções. O
pipeline TF-IDF com regressão logística foi planejado para a etapa seguinte; a API
continua persistindo placeholder, sem inferência de um classificador treinado.

O registro final da suíte contém **39 casos aprovados**. As evidências remotas do
exercício 3 mostram os **37 casos daquele momento**, incluindo falha controlada,
bloqueio de merge em `main` e recuperação. Elas não comprovam uma execução remota
posterior dos 39 casos.

O reteste ZAP passivo registrou zero alertas High, Medium e Low, com três tipos
informativos. A auditoria cobre o laboratório local e o tráfego descrito, sem
comprovar ausência de vulnerabilidades, TLS externo ou prontidão de uma API de
terceiros. Os documentos de detalhe preservam os limites e artefatos sanitizados.

## O que falta para entregar

1. Definir o colega e a URL/IP adversária, obter confirmação de acesso e registrar
   autorização e escopo no planejamento. Na ausência de colega, obter orientação
   do professor; nenhuma alternativa está presumida como aceita.
2. Revisar e publicar as mudanças no repositório, respeitando o workflow e a proteção
   de `main`; verificar os checks do PR correspondente antes da integração.
3. Preparar e revisar a entrega em PDF com o nome `leandro_medeiros_PB_TP3.PDF` e
   o link do repositório, conforme o formato e prazo definidos pelo professor.
   Este Markdown não constitui um PDF exportado ou uma submissão acadêmica.

## Fontes e uso de IA

Consolidação baseada no enunciado e orientações do TP3 e nos artefatos locais
vinculados. As fontes técnicas estão nos respectivos relatórios. Codex (OpenAI)
auxiliou na implementação, verificações e documentação dos exercícios; esta
consolidação distingue resultados registrados, propostas e pendências.

[Voltar ao README](../README.md) · [Glossário](glossario.md)
