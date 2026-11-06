# 🔄 TP3 — Integração contínua dos testes de segurança

O [workflow Security Tests](../../.github/workflows/security-tests.yml) executa a suíte a cada push e pull request, em todas as branches. O destino definido para a integração do TP3 é **`main`**. A implementação e a validação local estão prontas; execução remota e proteção efetiva da branch continuam pendentes de comprovação.

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
| Execução do workflow no GitHub | Pendente |
| Check obrigatório e bloqueio de merge em `main` | Pendente |

A [evidência local sanitizada](tp3-ci-validacao.txt) contém o resultado da suíte limpa e o resumo do experimento de falha. A [matriz de testes](tp3-testes.md) explica os cenários exercitados. O parser temporário não é dependência do projeto. Não foram executados actionlint nem o runner do GitHub localmente; parsing YAML não substitui validação e execução pelo GitHub.

O ambiente temporário não continha arquivos privados ou dataset. Os testes forneceram suas próprias variáveis de configuração. A instalação das dependências e as requisições ASGI foram executadas fora do sandbox restrito, conforme o diagnóstico do exercício 2. Isso não comprova que o runner remoto já executou.

## Ativação no GitHub e proteção de main

Depois de publicar o workflow na `feat/tp3`:

1. Abrir ou atualizar um PR **`feat/tp3` → `main`**, preferencialmente em rascunho enquanto o TP3 estiver em andamento. Conferir na aba Actions a execução de **Security Tests** para o commit atual e verificar `37 passed` no passo de testes.
2. Nas configurações do repositório, acessar **Settings → Branches → Add classic branch protection rule**, ou editar a regra existente que se aplica a `main`. Preservar proteções já configuradas.
3. Definir o padrão da branch como **`main`**, exigir pull request e habilitar **Require status checks to pass before merging**. Selecionar o check **`security-tests`**, proveniente do GitHub Actions. Ele poderá aparecer somente após a primeira execução. Se usar rulesets em vez de proteção clássica, aplicar o mesmo check a `main` e deixar o ruleset ativo.
4. Aplicar as restrições também a administradores, pela opção **Do not allow bypassing the above settings**, ou ausência de bypass no ruleset. Não habilitar force push ou exclusão da branch. Não é necessário exigir aprovação de outro revisor para este exercício individual.
5. Salvar a regra. Em PR temporário autorizado, comprovar que uma falha de teste deixa o job vermelho e impede o merge. Manter esse PR sem merge; corrigir a falha e verificar o novo check antes de qualquer integração. A falha controlada local desta etapa não substitui essa prova remota.

Não usar `pull_request_target` para executar código proposto nem conceder tokens de escrita ao job. As proteções dependem das permissões e dos recursos disponíveis no repositório; se a configuração não estiver disponível, registrar o impedimento e manter o requisito pendente.

## Evidências necessárias para fechar o exercício

Registrar o link da execução aprovada e seu commit, o link do PR, evidência da regra aplicada a `main` com `security-tests` obrigatório e evidência de merge bloqueado para um check reprovado. Não incluir tokens, credenciais ou arquivos privados nas capturas. Não considerar o exercício integralmente concluído antes de obter as evidências remotas.

Nesta etapa, não foram realizados commit, push, abertura de PR nem alteração das configurações remotas.

## Fontes e uso de IA

- [GitHub Docs: testes Python no Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
- [GitHub Docs: proteção de branches e checks obrigatórios](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [Action oficial checkout](https://github.com/actions/checkout) e [action oficial setup-python](https://github.com/actions/setup-python).
- Codex (OpenAI) auxiliou na configuração do workflow, na validação em ambiente limpo, no experimento local de falha e na documentação. Execução remota e bloqueio de merge não foram presumidos a partir dos resultados locais.
