# 🗺️ Diagrama de Fluxo de Dados (DFD) & Fronteiras de Confiança

O diagrama abaixo mapeia a arquitetura da API E-ComShield, evidenciando as zonas de risco e o fluxo de inferência preditiva.

## 📊 Diagrama Arquitetural (Mermaid)

```mermaid
flowchart TD
    subgraph TB_Internet [Fronteira de Confiança: Internet / Hostil]
        Client([Cliente / Atacante])
    end

    subgraph TB_EComShield [Fronteira de Confiança: Rede Interna E-ComShield]
        API[FastAPI Gateway]
        Auth[Módulo de Autenticação JWT]
        Predict[Módulo Preditivo NLP]
    end

    Client -- "1. Solicita Token (Credenciais)" --> API
    API -- "2. Valida Credenciais" --> Auth
    Auth -- "3. Emite JWT (HS256)" --> API
    API -- "4. Entrega JWT" --> Client

    Client -- "5. Envia Payload JSON + JWT Bearer" --> API
    API -- "6. Verifica Assinatura" --> Auth
    API -- "7. Encaminha Texto Sanitizado" --> Predict
    Predict -- "8. Retorna Intenção (Placeholder)" --> API
    API -- "9. Responde Cliente (HTTP 200)" --> Client
```
