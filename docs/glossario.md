# 📖 Glossário

- **EDA — Exploratory Data Analysis (Análise Exploratória de Dados):** investigação da estrutura, da qualidade e dos padrões dos dados antes da modelagem.
- **Intenção:** classe que descreve o objetivo da mensagem do cliente, como `complaint`.
- **API — Application Programming Interface (Interface de Programação de Aplicações):** conjunto de operações e contratos que permite a comunicação entre programas; no projeto, expõe rotas como `/predict`.
- **JSON — JavaScript Object Notation (Notação de Objetos JavaScript):** formato textual para representar dados estruturados, usado nos corpos das requisições e respostas da API.
- **JWT — JSON Web Token (Token Web JSON):** formato de token que transporta declarações, como sujeito (`sub`) e expiração (`exp`); no projeto, a API valida sua assinatura e prazo antes de confiar nessas informações.
- **BOLA — Broken Object Level Authorization (Falha de Autorização em Nível de Objeto):** vulnerabilidade que permite acessar um recurso sem a devida permissão, por exemplo, lendo um registro de outro usuário ao trocar seu identificador.
- **SQL — Structured Query Language (Linguagem de Consulta Estruturada):** linguagem para definir, consultar e modificar dados em bancos relacionais.
- **SQLModel:** biblioteca que combina modelos Python e consultas SQLAlchemy para persistência relacional.
- **CORS — Cross-Origin Resource Sharing (Compartilhamento de Recursos entre Origens):** mecanismo pelo qual o servidor informa ao navegador quais origens podem acessar suas respostas; não substitui autenticação.
- **IP — Internet Protocol (Protocolo de Internet):** protocolo de endereçamento e encaminhamento de pacotes entre redes; o endereço IP da conexão identifica a origem usada pelo limite de tentativas deste projeto.
- **Rate limiting:** limite de tentativas em uma janela de tempo; aqui, cinco requisições de autenticação por IP em 60 segundos.
- **Scan passivo:** análise de tráfego observado sem enviar payloads de exploração ativa. A cobertura depende das rotas visitadas.
- **p-valor:** probabilidade, sob a hipótese nula e as premissas do teste, de obter resultado ao menos tão extremo quanto o observado.

- **Regressão linear:** modelo que estima um alvo numérico por uma combinação linear dos atributos; simples com um atributo e múltipla com dois ou mais.
- **Pipeline:** sequência de transformações e estimador; mantém o ajuste do pré-processamento dentro dos dados de treino.
- **Baseline:** referência simples para comparação; na regressão do TP3, a previsão constante da média do treino.
- **R² — coeficiente de determinação:** comparação do erro quadrático do modelo com a variabilidade do alvo em torno da média do conjunto avaliado; pode ser negativo e não representa acurácia de classificação.
- **RMSE — Root Mean Squared Error (Raiz do Erro Quadrático Médio):** medida que penaliza erros grandes e tem a unidade do alvo; no TP3, caracteres.
- **Resíduo:** diferença entre valor observado e previsto; positivo indica subestimação.
- **Q-Q plot — Quantile-Quantile plot (Gráfico Quantil-Quantil):** comparação de quantis de duas distribuições; aqui, resíduos padronizados contra referência normal.
- **Homocedasticidade:** variância aproximadamente constante dos erros ao longo das condições avaliadas.
- **Vazamento de dados:** uso, no ajuste ou seleção, de informação que deveria ficar reservada à avaliação; textos repetidos entre treino e teste podem tornar a estimativa de generalização otimista.
