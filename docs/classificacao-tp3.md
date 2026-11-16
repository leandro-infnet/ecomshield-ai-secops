# Pergunta de classificação — TP3

## 1. Tarefa e dados

**Pergunta:** dado um texto de atendimento ao cliente, qual intenção do usuário ele expressa? A tarefa é **classificação supervisionada multiclasse de rótulo único**: aprender com pares de texto e intenção conhecida para atribuir uma das 27 classes a uma nova mensagem. Formalmente, $\hat f:\mathcal{X}\to\mathcal{Y}$, com $\mathcal{X}$ representando os textos e $\mathcal{Y}$ as intenções da tabela. Trata-se de um conjunto fechado; mensagens fora dessas classes ou com múltiplas intenções exigem tratamento futuro.

A entrada do dataset é `instruction`; o alvo é `intent`. `category` agrupa as intenções em 11 temas e não substitui o alvo. `response` e as demais colunas não serão usadas para inferir a intenção: o objetivo é reconhecer a mensagem recebida, sem depender de uma resposta já produzida. O campo correspondente na API é `texto_cliente`; ela ainda devolve placeholder, sem classificador integrado.

O CSV Bitext local contém **26.872 registros**, nenhum ausente, nenhuma instrução vazia e nenhuma linha inteira duplicada. Foram mantidas **2.237 repetições de texto**, correspondendo a **24.635 instruções distintas**, sem conflito de intenção para textos idênticos. As contagens abaixo usam todas as linhas, antes de qualquer divisão, com denominador $N=26\,872$. Identificação SHA-256 do arquivo:

`6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434`

## 2. Por que aprendizado supervisionado?

Os 26.872 pares rotulados permitem aprender associações entre conteúdo textual e classes e avaliar previsões em dados reservados. Estatísticas de frequência descrevem a base, mas não estabelecem, sozinhas, uma regra que reconheça intenções em textos novos. Prever sempre uma das classes com 1.000 registros acertaria apenas **3,72% desta base**, por contagem, sem avaliar generalização. Isso justifica investigar um classificador textual; não demonstra antecipadamente sua qualidade.

Na [regressão do exercício 1](eda/tp3-regressao.md), o alvo era comprimento, uma grandeza numérica. Intenções são categorias nominais, sem ordem ou distância: atribuir inteiros aos rótulos e arredondar regressão linear imporia relações arbitrárias e poderia gerar valores sem classe correspondente. R² e RMSE do comprimento não medem reconhecimento de intenção; a futura avaliação deverá usar métricas de classificação por classe e macro-F1.

## 3. Ambiguidades e limites

A distribuição próxima do equilíbrio (950–1.000 amostras por classe; razão máxima/mínima **1,053**) não garante precisão. Há proximidade entre `contact_customer_service` e `contact_human_agent`, e entre consultar regras, solicitar e acompanhar um reembolso. Esses limites deverão orientar a análise de erros; ausência de conflito em textos idênticos não comprova ausência de ambiguidade semântica ou de erros de anotação.

O corpus é **em inglês**, enquanto o atendimento pretendido pode receber português. Uso em português dependerá de dados ou adaptação e avaliação específicas. Repetições e possíveis templates restringem a independência das observações: textos iguais devem permanecer no mesmo grupo na separação treino/validação/teste, e similaridade entre templates merece investigação. O planejamento técnico é o próximo exercício; nenhum classificador foi treinado nesta etapa.

## 4. Classes e distribuição

Descrições em português interpretam os rótulos originais, que permanecem inalterados. Contagens calculadas por `groupby(["intent", "category"]).size()` e percentual $p_k=100\,n_k/N$, sendo $n_k$ a quantidade da classe. A [tabela CSV](eda/tp3-distribuicao-intencoes.csv) inclui categorias e percentuais com oito casas decimais. O arredondamento abaixo pode afetar a soma dos percentuais.

| Intenção | Descrição operacional | Quantidade | Percentual |
| --- | --- | ---: | ---: |
| `cancel_order` | Cancelar pedido | 998 | 3,71% |
| `change_order` | Alterar pedido | 997 | 3,71% |
| `change_shipping_address` | Alterar endereço de entrega | 973 | 3,62% |
| `check_cancellation_fee` | Consultar taxa de cancelamento | 950 | 3,54% |
| `check_invoice` | Verificar informações da fatura | 1000 | 3,72% |
| `check_payment_methods` | Consultar meios de pagamento | 999 | 3,72% |
| `check_refund_policy` | Consultar política de reembolso | 997 | 3,71% |
| `complaint` | Registrar reclamação | 1000 | 3,72% |
| `contact_customer_service` | Contatar o atendimento ao cliente | 1000 | 3,72% |
| `contact_human_agent` | Solicitar atendimento humano | 999 | 3,72% |
| `create_account` | Criar conta | 997 | 3,71% |
| `delete_account` | Excluir conta | 995 | 3,70% |
| `delivery_options` | Consultar modalidades de entrega | 995 | 3,70% |
| `delivery_period` | Consultar prazo de entrega | 999 | 3,72% |
| `edit_account` | Editar dados da conta | 1000 | 3,72% |
| `get_invoice` | Solicitar uma fatura | 999 | 3,72% |
| `get_refund` | Solicitar reembolso | 997 | 3,71% |
| `newsletter_subscription` | Gerenciar assinatura de newsletter | 999 | 3,72% |
| `payment_issue` | Resolver problema de pagamento | 999 | 3,72% |
| `place_order` | Fazer pedido | 998 | 3,71% |
| `recover_password` | Recuperar senha | 995 | 3,70% |
| `registration_problems` | Resolver problema de cadastro | 999 | 3,72% |
| `review` | Enviar avaliação | 997 | 3,71% |
| `set_up_shipping_address` | Cadastrar endereço de entrega | 997 | 3,71% |
| `switch_account` | Trocar a conta em uso | 1000 | 3,72% |
| `track_order` | Acompanhar pedido | 995 | 3,70% |
| `track_refund` | Acompanhar reembolso | 998 | 3,71% |
| **Total** | **27 classes** | **26.872** | **100%** |

## 5. Fontes e uso de IA

[Dataset Bitext](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset); [scikit-learn: aprendizado supervisionado](https://scikit-learn.org/stable/supervised_learning.html); [EDA local](eda/tp2.md) e [glossário](glossario.md). Codex (OpenAI) auxiliou no cálculo, interpretação e redação. Contagens foram recalculadas no CSV local; as descrições são interpretações do projeto, sujeitas à revisão do aluno.
