# 🧭 Planejamento T2 — classificação e preparação adversarial

O planejamento técnico do exercício 6 está concluído. **O exercício permanece
parcial:** ainda não há colega adversário, URL/IP nem confirmação de acesso à API
dele. Não há dispensa desse requisito registrada. T2 significa segundo trimestre;
este documento planeja a transição, sem antecipar treinamento ou ataques do TP4/TP5.

## 1. Problema e ponto de partida

A tarefa é prever uma intenção entre 27 classes a partir da mensagem do cliente.
A [pergunta de classificação](classificacao-tp3.md) concentra as definições,
distribuição e identificação do dataset: 26.872 exemplos Bitext em inglês, com
24.635 textos distintos por igualdade exata. A entrada será `instruction` e o
alvo, `intent`; `response`, `category` e `flags` não serão atributos preditivos.

Hoje, a API registra `track_refund_placeholder` com `confianca=0.0`. A
[regressão numérica](eda/tp3-regressao.md) prevê comprimento de texto e não fornece
um classificador de intenções. As decisões seguintes são propostas para T2,
sem resultados de classificação medidos.

## 2. Modelo e representação do texto

O candidato principal será um pipeline de **TF-IDF + regressão logística**.
TF-IDF (Term Frequency–Inverse Document Frequency, frequência do termo ponderada
pelo inverso da frequência nos documentos) representa textos por vetores esparsos,
reduzindo o peso de termos muito disseminados. A regressão logística é um
classificador, apesar do nome: estima probabilidades das classes a partir desses
atributos, em vez de prever um comprimento numérico.

Essa combinação é uma referência inicial de custo moderado, com associação entre
termos e classes inspecionável pelos coeficientes. Usaremos palavras isoladas e
pares consecutivos de palavras (`ngram_range=(1, 2)`) para representar expressões
como solicitar ou acompanhar reembolso. O ponto de partida será
`TfidfVectorizer(lowercase=True, min_df=2)`, sem remoção automática de stopwords:
negações podem alterar a intenção. Essas escolhas deverão ser revistas na validação;
termos raros podem ser relevantes. Não há benefício demonstrado antecipadamente.

A configuração inicial da regressão logística será `C=1.0`, `max_iter=1000` e
sem ponderação de classes. O limite de iterações exige conferir convergência;
não garante ajuste adequado. A razão entre maior e menor classe é apenas 1,053,
portanto não há motivo inicial para balanceamento artificial. Eventual alteração
dependerá dos erros por classe no desenvolvimento.

Como alternativa, avaliaremos **LinearSVC**, uma SVM linear (Support Vector
Machine, máquina de vetores de suporte) que aprende fronteiras por margem, usando
a mesma representação e partições. Um `DummyClassifier(strategy="most_frequent")`
ajustado apenas no treino fornecerá a referência mínima. CountVectorizer, que
conta ocorrências sem ponderação IDF, poderá servir de comparação se a análise
de erros justificar; não é necessário ampliar a busca antes dessa evidência.

## 3. Separação, treinamento e avaliação previstos

O protocolo deverá ser reproduzível e evitar que cópias de uma mensagem apareçam
nos dois lados da avaliação:

1. Conferir o hash do CSV contra o documento de classificação; verificar nulos,
   textos vazios e conflitos de rótulo novamente antes de treinar.
2. Criar grupos pela mensagem em minúsculas, espaços consecutivos reduzidos e
   espaços nas extremidades removidos. Essa chave serve à separação; não substitui
   o texto original. Investigar grupos com rótulos conflitantes antes de prosseguir.
3. Reservar aproximadamente 20% para teste com `StratifiedGroupKFold`, cinco
   partições, embaralhamento e `random_state=42`. No restante, usar quatro
   partições do mesmo método para separar validação e treino, buscando cerca de
   60%/20%/20% do total. Escolher deterministicamente a primeira partição em ambos
   os passos. Os grupos podem impedir proporções exatas.
4. Registrar índices localmente, hash, versão das bibliotecas, contagens por classe
   e grupo. Verificar que não há grupo compartilhado entre partições e que as 27
   classes estão representadas. Não publicar textos nem identificadores sensíveis.
5. Ajustar vocabulário, IDF e classificador somente no treino, dentro do pipeline.
   Comparar candidatos na mesma validação. Não usar o teste para escolher modelo,
   atributos ou hiperparâmetros.
6. Após fixar as decisões, reajustar o pipeline em treino mais validação e avaliar
   uma vez no teste reservado. Registrar o protocolo e os resultados completos.

A métrica principal será **macro-F1**, média do F1 por classe com peso igual entre
elas. Também serão registrados precisão, recall, F1 e suporte por intenção,
matriz de confusão, acurácia e comparação com o classificador de referência.
Tempo de ajuste, latência de inferência e tamanho do artefato serão medidos no
ambiente descrito, sem impor metas numéricas ainda sem contexto de uso.

O agrupamento proposto reduz vazamento por cópias normalizadas; não impede
paráfrases ou templates semelhantes entre partições. Será necessário examinar
esses casos e as confusões entre intenções próximas. Não há expectativa de
desempenho em português comprovada por dados em inglês. Mensagens fora das 27
classes ou com múltiplas intenções exigirão avaliação específica antes do uso real.

## 4. Integração futura e preservação dos contratos

O treinamento ocorrerá fora do serviço. O pipeline completo será salvo como
artefato confiável e carregado uma vez por processo, no ciclo de vida da API.
Uma requisição executará apenas transformação e inferência. A versão do artefato
deverá acompanhar hash do dataset, classes, normalização, partições, métricas e
versões das dependências. Artefatos baseados em pickle/joblib podem executar código
ao carregar: usar somente arquivos de origem controlada, nunca uploads de clientes.

A integração deverá preservar o JSON `texto_cliente`, os limites atuais de 5 a
100 caracteres, a rejeição de campos extras, JWT, propriedade do registro e os
campos de saída `id`, `intencao_prevista` e `confianca`. Esses limites serão
reavaliados conforme os dados de uso; a mudança de contrato exigirá documentação
e testes próprios. Falha de carregamento do modelo deverá impedir a inicialização
do serviço preditivo, sem apresentar placeholder como inferência real.

Na regressão logística, `confianca` poderá receber a probabilidade estimada da
classe escolhida, deixando claro que probabilidade estimada não garante calibração.
A margem de `LinearSVC.decision_function` não é probabilidade: se a SVM for
selecionada, será necessário planejar calibração dentro dos dados de desenvolvimento
ou revisar explicitamente o contrato antes da integração, sem usar o teste para isso.

Registros antigos de placeholder precisam continuar identificáveis. Uma eventual
inclusão de versão do modelo na persistência exigirá migração explícita, sem
reinterpretar esses registros como previsões treinadas. A futura validação deverá
cobrir contrato, inferência, carregamento inválido, persistência, autorização e
regressão da suíte de segurança. Logs não deverão registrar mensagens, senhas ou
tokens. Nenhuma dessas alterações na API foi implementada neste exercício.

## 5. Acordo adversarial — pendência obrigatória

O aluno informou que ainda não possui colega adversário. O laboratório próprio
em loopback, descrito na [auditoria final](security/tp3-auditoria-final.md), comprova
preparação local; não identifica a API adversária e não substitui o acordo entre
equipes. Não houve teste contra terceiros nesta etapa.

| Informação necessária | Situação |
| --- | --- |
| Nome do colega/equipe responsável pela API adversária | Pendente de definição |
| URL ou IP, protocolo e portas do alvo | Pendente |
| Confirmação do colega de que o acesso está disponível | Pendente |
| Autorização explícita e registro do acordo | Pendente |
| Rotas permitidas, técnicas aceitas e exclusões | Pendente de acordo |
| Janela, limites de requisições e condições de interrupção | Pendente de acordo |
| Contas e dados sintéticos, entregues por canal seguro | Pendente |
| Contato responsável para interrupção e comunicação de achados | Pendente |

Para concluir esse requisito, o aluno deverá combinar a parceria com um colega ou
solicitar ao professor orientação sobre sua ausência. Caso o professor autorize
uma alternativa, registrar a decisão e o escopo efetivamente aprovado, sem presumir
equivalência. Em seguida, preencher a tabela e obter a confirmação de acesso antes
da entrega, conforme a exigência acadêmica.

No TP4/TP5, os testes poderão investigar autenticação, autorização por objeto,
validação e configuração HTTP, conforme o acordo. Qualquer execução dependerá de
alvo, autorização e limites confirmados; não se prevê indisponibilidade, alteração
destrutiva ou uso de dados reais. Os resultados deverão registrar reprodução,
impacto, correção e reteste sanitizados. Este plano não concede autorização de teste.

## 6. Fontes e uso de IA

- [scikit-learn: extração de atributos de texto](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction).
- [Regressão logística](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) e [SVM linear](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html).
- [Separação estratificada por grupos](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).
- [Persistência de modelos e limitações de segurança e compatibilidade](https://scikit-learn.org/stable/model_persistence.html).
- [Glossário do projeto](glossario.md) e [consolidação do TP3](tp3-relatorio.md).

Codex (OpenAI) auxiliou na escolha e justificativa das propostas e na redação.
Nenhum classificador foi treinado, métrica de classificação foi produzida ou
acesso adversarial foi confirmado na elaboração deste documento.
