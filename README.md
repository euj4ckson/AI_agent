# Modular AI Agent (LLM + RAG + Memória)

Projeto de referência para um agente de IA modular, escalável e pronto para produção, com FastAPI, OpenAI, RAG e memória persistente.

## Visão geral

Este agente:
- Entende linguagem natural e toma decisões com base em contexto
- Usa ferramentas externas via tool calling
- Mantém histórico de conversas (curto e longo prazo)
- Consulta base vetorial via RAG
- Permite troca fácil de provedor LLM

## Stack

- Python 3.11+
- FastAPI
- OpenAI (LLM + Embeddings)
- ChromaDB (vetores)
- SQLite (memória persistente)
- Pydantic + type hints
- Pytest

## Estrutura de pastas

```
app/
  api/            # rotas FastAPI
  agent/          # loop do agente e prompts
  core/           # config, logging, LLM
  memory/         # memória curta e longa
  rag/            # RAG e vetor store
  tools/          # ferramentas do agente
  services/       # regras de negócio
  models/         # schemas Pydantic
  tests/          # testes automatizados
```

## Instalação

1) Criar ambiente virtual e instalar dependências:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure as variáveis:

```
copy .env.example .env
```

Edite `.env` e informe `OPENAI_API_KEY`.

3) Rodar a API:

```
uvicorn app.main:app --reload
```

## Endpoints

- `POST /chat` envia mensagens ao agente
- `POST /documents` adiciona documentos à base RAG
- `GET /memory/{user_id}` retorna memórias do usuário

## Como adicionar novas tools

1) Implemente uma classe em `app/tools/implementations.py` herdando `Tool`.
2) Registre a tool no `ToolRegistry` em `app/tools/registry.py`.
3) Exponha no agente via `build_tool_registry()` em `app/services/chat_service.py`.

## Como trocar o modelo LLM

- Ajuste `OPENAI_MODEL` em `.env`.
- Para trocar o provedor, implemente outro cliente em `app/core/llm.py` que satisfaça `LLMClient` e troque na criação do agente em `app/services/chat_service.py`.

## Alternativa gratuita (Ollama)

Você pode rodar um modelo local sem limite de créditos usando Ollama.

1) Instale Ollama: https://ollama.com  
2) Baixe modelos:

```
ollama pull llama3.1
ollama pull nomic-embed-text
```

3) Em `.env`, configure:

```
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1
OLLAMA_EMBED_MODEL=nomic-embed-text
```

4) Reinicie o servidor.

## Testes

```
pytest
```

Os testes usam implementações fake de LLM e embeddings, sem chamadas externas.

## Produção

- Use `ENVIRONMENT=production`
- Configure logs centralizados
- Troque SQLite por PostgreSQL se necessário (ajuste `MEMORY_DB_URL`)
- Defina limites de taxa e autenticação nas rotas
