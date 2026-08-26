# 🛡️ E-ComShield API (Projeto de Bloco - TP1)

API assíncrona para atendimento automatizado de E-commerce, análise exploratória de dados e arquitetura defensiva contra vulnerabilidades de injeção e quebra de controle de acesso (OWASP API Top 10).

---

## 📑 Sumário Executivo

- [📊 1. Dataset & Domínio do Sistema](#-1-dataset--domínio-do-sistema)
- [📁 2. Estrutura do Projeto](#-2-estrutura-do-projeto)
- [⚙️ 3. Instalação & Execução](#️-3-instalação--execução)
- [📐 4. Arquitetura & DFD](./docs/architecture/dfd.md)
- [🔒 5. Modelagem de Ameaças (STRIDE)](./docs/security/stride.md)
- [📈 6. Análise Exploratória (Notebook)](./notebooks/01_eda_ecomshield.ipynb)

---

## 📊 1. Dataset & Domínio do Sistema

- **Nome:** Bitext Customer Support LLM Chatbot Training Dataset
- **Fonte:** Hugging Face Datasets
- **Link Oficial:** [huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)
- **Licença:** Apache License 2.0 (Permissiva para uso acadêmico e comercial)
- **Amostras:** 26.872 registros (5 colunas: `flags`, `instruction`, `category`, `intent`, `response`)
- **Justificativa Técnica:** Dataset limpo, balanceado e estruturado especificamente para suporte de comércio eletrônico (intenções de reembolso, cancelamento, alteração cadastral), viabilizando o treinamento futuro de agentes inteligentes sem viés amostral.

---

## 📁 2. Estrutura do Projeto

```bash
.
├── README.md
├── requirements.txt
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── api
│   │   └── routes
│   │       ├── auth.py
│   │       ├── health.py
│   │       └── predict.py
│   ├── core
│   │   └── security.py
│   ├── models
│   │   └── schemas.py
│   └── services
├── data
│   ├── processed
│   └── raw
│       └── bitext_intent.csv
├── docs
│   ├── architecture
│   │   ├── dfd.md
│   │   └── ecomshield-ai-secops.png
│   └── security
│       └── stride.md
└── notebooks
    └── 01_eda_ecomshield.ipynb
```

---

## ⚙️ 3. Instalação & Execução

### Pré-requisitos

* Python 3.11+ ou WSL 2 (Ubuntu 24.04 LTS)

### Passo a Passo

1. Clone o repositório e acesse o diretório:

```bash
git clone https://github.com/leandro-infnet/ecomshield-ai-secops.git
cd ecomshield-ai-secops
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente criando um arquivo `.env` na raiz:

```env
SECRET_KEY=chave_secreta_super_segura_desenvolvimento_infnet
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Execute a API com recarregamento automático:

```bash
uvicorn app.main:app --reload
```

6. Acesse a documentação Swagger interativa em: `http://127.0.0.1:8000/docs`

---

**OBS**: Para ver os tópicos 4, 5 e 6 do **Sumário Executivo**, clique nos links do próprio Sumário para ser redirecionado aos respectivos arquivos.
