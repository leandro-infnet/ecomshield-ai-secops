# 🔐 Ameaças e controles do TP2

A análise usa [STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats), taxonomia de falsificação de identidade, adulteração, repúdio, divulgação, negação de serviço e elevação de privilégio. O [DFD](../architecture/dfd.md) delimita os componentes realmente presentes. Controles implementados são distintos de medidas necessárias antes de produção.

| Ameaça | Cenário | Controle verificado ou limite |
| --- | --- | --- |
| Spoofing | Bearer arbitrário ou JWT adulterado em `/predict` | `jwt.decode` fixa HS256 e exige `sub`/`exp`; testes cobrem ausente, arbitrário, adulterado e expirado. |
| Tampering | Campo extra altera o contrato | Pydantic `extra='forbid'` responde 422; JWT não protege o body HTTP. TLS é necessário para trânsito fora do host. |
| Repudiation | Usuário nega criação de predição | O registro tem `owner_id`, mas não existe trilha de auditoria imutável. |
| Information disclosure | Usuário troca ID para ler registro alheio | Consulta SQLModel filtra `id` e `owner_id`; outro usuário recebe 404. O banco local e backups precisam de proteção operacional. |
| Denial of service | Força bruta no login | Cinco tentativas/IP/minuto em memória, com proxy headers desabilitados no comando local; teste cobre `X-Forwarded-For` variável. Sem limite distribuído, quotas de inferência ou proteção contra tráfego volumoso. |
| Elevation of privilege | Cliente manipula `sub`/ID | A assinatura é validada e o proprietário vem do usuário encontrado no banco, não do body. Não há funções administrativas. |

## 🧩 Confidencialidade, integridade e disponibilidade por componente

| Componente | Confidencialidade | Integridade | Disponibilidade |
| --- | --- | --- | --- |
| Cliente e rede | TLS deve ser fornecido em implantação; HTTP local não cifra | TLS deve proteger body e token em trânsito | Limites de conexão dependem da infraestrutura |
| FastAPI | Respostas não expõem `texto_cliente` nem hash de senha | Pydantic rejeita extras; headers e CORS limitam comportamento de navegador | Sem quota geral ou timeouts de infraestrutura |
| Autenticação JWT | Segredo vem do ambiente; senha tem hash com salt | Assinatura e expiração verificadas | Limite por IP reduz tentativas rápidas, apenas por processo |
| Placeholder de predição | Não há prompt nem modelo a extrair | Texto não executa comandos; intenção é fixa | Processamento leve, sem proteção completa contra DoS |
| SQLite | Arquivo em `data/processed/`, ignorado pelo Git | Chaves de proprietário e consultas parametrizadas; sem migrações | Banco local é ponto único de falha |
| Dataset de EDA | Arquivo bruto ignorado pelo Git | Análise preserva original e mede duplicatas | Reprodutor precisa obter o arquivo externo |

Não há agente com ferramentas, pesos treinados ou prompt de sistema nesta etapa; riscos de prompt injection e envenenamento de modelo serão relevantes quando esses componentes existirem. O limite de 100 caracteres só contém o tamanho individual do payload. O [relatório ZAP](zap-findings.md) cobre a auditoria passiva e suas limitações.
