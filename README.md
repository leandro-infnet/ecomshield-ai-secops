# 🛡️ E-ComShield API (Projeto de Bloco - TP1)

Projeto focado em atendimento automatizado de E-commerce, análise de dados e segurança de APIs (Defesa contra IDOR e injeções).

## 📑 Sumário Executivo

* 📊 [Análise Exploratória de Dados (EDA)](./notebooks/01_eda_ecomshield.ipynb)
* 📐 [Arquitetura & DFD](./docs/architecture/dfd.md)
* 🔒 [Modelagem de Ameaças (STRIDE)](./docs/security/stride.md)
* 🚀 [Instruções de Instalação e Execução](#-instalação)

## 🛠️ Stack Tecnológica
* **Backend:** FastAPI, Uvicorn, Python 3.12+
* **Dados:** Pandas, Seaborn
* **Segurança:** JWT (OAuth2PasswordBearer), OWASP Top 10 mitigations

## ⚙️ Instalação (Ambiente Local)
1. Clone o repositório.
2. Crie o ambiente virtual: `python -m venv venv`
3. Ative: `source venv/bin/activate` (Linux/WSL)
4. Instale as dependências: `pip install -r requirements.txt`
