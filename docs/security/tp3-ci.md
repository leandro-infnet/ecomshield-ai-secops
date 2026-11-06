# 🔄 TP3 — Integração contínua dos testes de segurança

O [workflow Security Tests](../../.github/workflows/security-tests.yml) executa a suíte a cada push e pull request, em todas as branches. O destino definido para a integração do TP3 é **`main`**. **Exercício 3 concluído nas evidências registradas:** execução remota aprovada, proteção aplicada, regressão bloqueada e recuperação verificada. O [índice de evidências](../ci/index.md) reúne capturas, links das execuções e encerramento do PR temporário sem merge.

## Funcionamento

Integração contínua (CI, Continuous Integration) é a execução automática de verificações sobre alterações do código. Aqui, um único job, **`security-tests`**, usa runner `ubuntu-latest`, configura Python 3.14, instala `requirements.txt` e executa:

```bash
python -m pytest tests/ -v
```

As actions oficiais `checkout@v7` e `setup-python@v7` seguem as versões documentadas pelos mantenedores na consulta desta etapa. Python 3.14 acompanha o ambiente local; não usamos o Python 3.11 ilustrativo dos slides porque NumPy e SciPy fixados exigem pelo menos 3.12.

O workflow usa permissão `contents: read`, não persiste credenciais do checkout, mantém cache do pip associado ao arquivo de dependências e limita a duração do job a dez minutos. Não filtra caminhos ou branches, não ignora erros e não condiciona a etapa de testes. Falha de instalação ou código de saída não zero do pytest faz o job falhar. O nome `security-tests` deve permanecer estável para ser selecionado como check obrigatório.

Não há publicação da aplicação neste exercício. A suíte usa dados sintéticos e SQLite temporário e não precisa de `.env`, segredos do repositório, banco persistente ou dataset bruto.

## Validação realmente executada

| Verificação | Resultado |
| --- | --- |
| Parsing YAML e inspeção dos eventos, permissões e comandos | Aprovado; sem `continue-on-error` ou condição que pule os testes |
| Instalação de `requirements.txt` em venv novo, com cópia apenas de `app/`, `tests/` e requisitos | Aprovada |
| `python -m pytest tests/ -v` nesse ambiente limpo | **37 passed in 6.50s** |
| `python -m pip check` nesse ambiente | Nenhuma dependência inconsistente |
| Desativar verificação de expiração JWT apenas na cópia temporária | **2 failed, 35 deselected**, código de saída **1**, nos dois casos de token expirado; cópia restaurada ao final |
| Execução do workflow no GitHub | Aprovada em push e pull_request: 37 testes passaram após a restauração |
| Check obrigatório e bloqueio de merge em `main` | Verificados no PR #13: falha de expiração JWT reprovou os checks Required e desabilitou o merge |

A [evidência local sanitizada](tp3-ci-validacao.txt) contém o resultado da suíte limpa e o resumo do experimento de falha. A [matriz de testes](tp3-testes.md) explica os cenários exercitados. O parser temporário não é dependência do projeto. Não foram executados actionlint nem o runner do GitHub localmente; parsing YAML não substitui validação e execução pelo GitHub.

O ambiente temporário não continha arquivos privados ou dataset. Os testes forneceram suas próprias variáveis de configuração. A instalação das dependências e as requisições ASGI foram executadas fora do sandbox restrito, conforme o diagnóstico do exercício 2. Esses registros locais são complementados pelas capturas remotas do experimento, vinculadas no índice.

## Configuração aplicada e prova remota

A regra de `main` exige PR e o check `security-tests` da origem GitHub Actions, com branch atualizada e sem bypass inclusive para administradores. Aprovação de outro revisor, force push e exclusão da branch estão desabilitados. A [sequência de capturas](../ci/index.md) documenta a configuração e seu efeito no PR #13.

O aluno criou a branch temporária `ci/validar-bloqueio-tp3` a partir da `feat/tp3` e abriu o [PR #13 para main](https://github.com/leandro-infnet/ecomshield-ai-secops/pull/13). No commit `6bae619`, desativou exclusivamente a verificação de expiração JWT para provocar uma regressão controlada. Os dois casos de token expirado falharam; os outros 35 passaram. Tanto o evento push quanto pull_request terminaram com código 1. O PR mostrou os checks como Required e o merge desabilitado.

No commit `8e7fb7e`, a validação foi restaurada. As novas execuções passaram com **37 testes**, em 11,76 s no push e 10,56 s no pull_request. Os checks voltaram a aprovar, e o PR foi **fechado sem merge**, conforme a captura final. Links de runs, jobs e imagens têm fonte principal no [índice de evidências](../ci/index.md), evitando duplicação de identificadores.

## Limites e manutenção

A consolidação confere as capturas fornecidas pelo aluno; não representa nova execução do agente nem consulta autenticada do estado atual. O PR e a execução consultados não puderam ser abertos pela ferramenta de navegação. As evidências são suficientes para o requisito acadêmico exercitado, sem afirmar cobertura de todas as formas de contorno, auditoria completa da API ou deployment.

Manter o nome do job e a exigência do check na proteção de `main`. Mudanças no workflow ou na regra exigem nova conferência do vínculo. Não usar `pull_request_target` para executar código proposto nem conceder tokens de escrita ao job. O experimento de falha foi encerrado e não deve ser integrado ao PR principal do TP3.

## Fontes e uso de IA

- [GitHub Docs: testes Python no Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
- [GitHub Docs: proteção de branches e checks obrigatórios](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [Action oficial checkout](https://github.com/actions/checkout) e [action oficial setup-python](https://github.com/actions/setup-python).
- Codex (OpenAI) auxiliou na configuração do workflow, na validação em ambiente limpo, no experimento local de falha e na documentação. As operações remotas e capturas foram realizadas pelo aluno e revisadas na consolidação; execução remota e bloqueio de merge estão documentados separadamente dos resultados locais.
