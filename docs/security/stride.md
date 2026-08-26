# 🔐 Modelagem de Ameaças (STRIDE) & Visão de Segurança E-ComShield

Documento técnico da API de Suporte (E-ComShield) detalhando a <abbr title="Superfície de Ataque: conjunto de pontos de inserção de dados e interação">Superfície de Ataque</abbr>, a <abbr title="Matriz de avaliação de risco baseada em Damage, Reproducibility, Exploitability, Affected Users e Discoverability">Matriz DREAD</abbr> e a taxonomia <abbr title="Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege">STRIDE</abbr>.

---

## 🗺️ 1. Superfície de Ataque (Attack Surface)

| Vetor de Entrada | Protocolo | Formato | Componente Alvo | Risco Potencial Primário |
| :--- | :--- | :--- | :--- | :--- |
| `POST /auth/token` | HTTP | `Form URL Encoded` | `auth.py` | Ataque de Força Bruta, Spoofing |
| `POST /predict` | HTTP | `application/json` | `predict.py` | Injeção de Prompt, Negação de Serviço (DoS), Tampering |
| `GET /health` | HTTP | *Nenhum* | `health.py` | Information Disclosure (Banner Grabbing) |

---

## 🔍 2. Análise Detalhada de Ameaças pelo Modelo STRIDE

De acordo com a taxonomia oficial, estruturamos os cenários de ameaça e seus respectivos controles de segurança.

### 🎭 S - Spoofing (Falsificação de Identidade)
Ação destinada a acessar e usar as credenciais de outro usuário.
* **Cenário:** Atacante tenta consumir a rota preditiva forjando um Token JWT genérico.
* **Controle de Segurança (Autenticação):** A API exige o esquema `OAuth2PasswordBearer`. O algoritmo HS256 rejeita tokens cuja assinatura não coincida com a `SECRET_KEY` do servidor.

### ✏️ T - Tampering (Adulteração de Dados)
Ação com a intenção de modificar maliciosamente dados em trânsito.
* **Cenário:** Interceptação do *payload* `PredictRequest` alterando a intenção do usuário no meio do tráfego.
* **Controle de Segurança (Integridade):** Protocolos resistentes à adulteração (TLS/HTTPS em produção) e uso de MACs (Message Authentication Codes) incorporados na assinatura do JWT.

### 📜 R - Repudiation (Não-Repúdio)
Ação destinada a realizar operações em um sistema sem capacidade de rastrear a autoria.
* **Cenário:** Cliente submete comandos de "estorno" (via IA) e nega a ação posteriormente.
* **Controle de Segurança (Não-repúdio):** O JWT amarrou a requisição ao campo `sub` (subject). Futuras trilhas de auditoria registrarão essa dependência.

### 👁️ I - Information Disclosure (Divulgação de Informação)
Ação com intenção de ler dados ou arquivos sem permissão de acesso.
* **Cenário:** Acesso indevido ao dataset bruto que treinou o modelo, contendo potenciais PIIs (Personal Identifiable Information).
* **Controle de Segurança (Confidencialidade):** Proteção de segredos via `.env` e isolamento dos dados locais (`data/raw/`) configurado estritamente no `.gitignore`.

### 💥 D - Denial of Service (Negação de Serviço)
Ação que tenta negar o acesso a usuários legítimos, exaurindo o servidor.
* **Cenário:** Disparo de *payloads* HTTP com 50.000 caracteres visando travar a RAM no processamento de linguagem natural.
* **Controle de Segurança (Disponibilidade):** Filtragem estrita na borda. O modelo Pydantic impõe `max_length=100`, derivado estatisticamente da Análise Exploratória (EDA).

### 👑 E - Elevation of Privilege (Elevação de Privilégio)
Ação para obter acesso privilegiado a recursos.
* **Cenário:** Usuário tenta manipular os *claims* internos do JWT para acessar ferramentas agênticas exclusivas de administradores.
* **Controle de Segurança (Autorização):** Adoção do princípio do menor privilégio. O token emitido no TP1 é atômico e não possui escopos de elevação configurados.

---

## 📊 3. Matriz de Avaliação de Riscos (DREAD)

Fórmula de Risco Relativo: $Risk = \frac{D + R + E + A + D}{5}$

| Ameaça Modelada | D | R | E | A | D | DREAD (Total) | Mitigação Atual |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| **DoS via Payload Massivo (Buffer Exaustion)** | 9 | 10 | 10 | 10 | 8 | **9.4** (Crítico) | Mitigado por `PredictRequest(max_length=100)` |
| **Spoofing de Token JWT (Falsificação)** | 8 | 7 | 4 | 5 | 5 | **5.8** (Médio) | Mitigado pela força criptográfica do HMAC-SHA256 |
| **Information Disclosure via Tracebacks** | 6 | 9 | 9 | 3 | 7 | **6.8** (Médio) | Parcial. Exige `DEBUG=False` em produção |

---

## 🛡️ 4. Análise Formal da Tríade CIA por Componente Arquitetural

| Componente / Ativo | 🔒 Confidencialidade (C) | 🛡️ Integridade (I) | ⚡ Disponibilidade (A) |
| :--- | :--- | :--- | :--- |
| **1.0 FastAPI Gateway** | Tráfego encapsulado via TLS (HTTPS). Sem retenção de logs em texto puro com dados sensíveis. | Validação estrita de contratos via Pydantic (`PredictRequest`) para evitar adulteração de payload. | Mitigação de sobrecarga por meio de limites de caracteres e arquitetura assíncrona ASGI. |
| **2.0 Módulo JWT** | Chave simétrica `SECRET_KEY` isolada em memória volátil; nunca exposta via resposta HTTP. | Assinatura HMAC-SHA256 invariável; qualquer modificação de bits invalida o token. | Emissão rápida sem dependência de consultas bloqueantes de banco de dados (estateless). |
| **3.0 Motor NLP (IA)** | Ocultamento do algoritmo e do prompt base contra extração (*Model Inversion*). | Imutabilidade dos pesos pré-treinados contra ataques de envenenamento (*Data Poisoning*). | Proteção contra exaustão de inferência via validação de payload máximo de 100 caracteres. |
| **Data Store (`.env` / Pesos)** | Arquivo `.env` protegido por permissões POSIX (`chmod 600`) e segregado no `.gitignore`. | *Checksums* criptográficos (SHA-256) para garantir a não modificação dos arquivos locais. | Acesso em tempo constante $O(1)$ pelo sistema de arquivos no arranque da aplicação. |
