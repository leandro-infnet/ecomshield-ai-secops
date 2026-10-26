# 📊 Relatório de análise exploratória — TP2

## Problema

O E-ComShield pretende classificar a intenção de mensagens de atendimento no TP3. Este relatório investiga a distribuição dos rótulos, o comprimento dos textos e a hipótese do TP1 de que mensagens de reclamação ou contato com atendimento são mais curtas. A análise é exploratória; nenhum classificador foi treinado.

## 🗂️ Dados

O [dataset Bitext Customer Support LLM Chatbot Training Dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) contém 26.872 registros e cinco colunas originais: `flags`, `instruction`, `category`, `intent` e `response`. A coluna `instruction` é a mensagem e `intent` é o rótulo futuro. Há 27 intenções e 11 categorias. O arquivo bruto local em `data/raw/bitext_intent.csv` é ignorado pelo Git; quem reproduzir precisa obtê-lo da fonte citada e conferir sua versão.

A inspeção executada no [notebook](../../notebooks/01_eda_ecomshield.ipynb) encontrou zero valores ausentes, zero instruções vazias e zero linhas inteiras duplicadas. Há 2.237 repetições da coluna `instruction`, mas nenhuma instrução repetida com rótulos `intent` diferentes. As repetições foram mantidas porque removê-las sem investigar sua origem mudaria a distribuição; devem ser agrupadas ao dividir treino e teste para evitar vazamento.

## 🔎 Análise

Criamos contagens vetorizadas de caracteres, palavras e sinais de pontuação por instrução. O comprimento vai de 6 a 92 caracteres. O notebook apresenta barras das intenções mais frequentes, histograma de comprimento, boxplot das cinco intenções mais frequentes, mapa de calor Seaborn da correlação de Pearson e dispersão de palavras versus caracteres em amostra reproduzível de 2.000 linhas (`random_state=42`). Intenções não foram codificadas como números para correlação, pois seus códigos seriam arbitrários.

A correlação entre caracteres e palavras é $r=0{,}813$; entre caracteres e pontuação é $r=0{,}183$. São associações entre características extraídas do mesmo texto, sem implicação causal nem prova de capacidade de classificação.

### Hipótese formal do TP1

Definimos o grupo focal como `complaint` e `contact_customer_service` ($n=2.000$) e o grupo de comparação como as demais intenções ($n=24.872$). Aplicamos [Mann–Whitney U unilateral](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html), com alternativa `less` e método assintótico, pois a hipótese do TP1 afirmava que o grupo focal tende a mensagens mais curtas. A hipótese nula $H_0$ é ausência de deslocamento para valores menores; $H_1$ é deslocamento para comprimentos menores. O nível de decisão foi $\alpha=0{,}05$.

| Grupo | n | Mediana | Média |
| --- | ---: | ---: | ---: |
| Reclamação ou contato com atendimento | 2.000 | 52 | 49,14 |
| Demais intenções | 24.872 | 48 | 46,71 |

O resultado foi $U=28.909.189{,}5$ e $p=1{,}0$ (arredondado). Logo, não rejeitamos $H_0$ nessa direção. As medianas observadas apontam no sentido oposto ao previsto: essas mensagens não foram mais curtas neste conjunto. O p-valor não é a probabilidade de $H_0$ ser verdadeira, nem informa sozinho o tamanho do efeito.

## 💡 Insights principais

1. O teste não corroborou a hipótese de mensagens de reclamação/contato mais curtas. O boxplot isolado do TP1 não bastava para inferir essa tendência.
2. Comprimento de caracteres e palavras são redundantes em parte. Na classificação do TP3, avaliar sua contribuição incremental será mais útil do que presumir poder preditivo pela correlação.
3. A presença de textos repetidos requer divisão cuidadosa antes de medir desempenho. Balanceamento aproximado de classes no dataset não garante precisão em produção.

## Limitações

O dataset pode conter templates e não representar a distribuição de mensagens reais. A comparação foi escolhida após exploração do TP1, e observações repetidas podem comprometer a independência assumida pelo teste. Não houve correção por múltiplas hipóteses nem avaliação de efeito prático. O máximo observado de 92 caracteres não prova que mensagens legítimas futuras caibam no limite demonstrativo de 100 caracteres da API. Esse limite reduz apenas o tamanho individual do payload; não neutraliza ataques de negação de serviço.

## 🧭 Próximos passos

No TP3, definir divisão estratificada que mantenha textos idênticos ou templates no mesmo conjunto, construir baseline de classificação de `intent`, medir precisão, recall e F1 por classe e analisar erros em mensagens curtas e longas. Rever o limite de entrada com dados de operação autorizados antes de uso real.

## Fontes e uso de IA

- [Fonte do dataset Bitext](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset).
- [Documentação SciPy do teste Mann–Whitney U](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html).
- Codex (OpenAI) auxiliou na implementação, execução e redação. Os números acima foram obtidos da execução local do notebook e conferidos contra o dataset disponível no workspace.
