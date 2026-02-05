from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = Field(default="ModularAI", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    memory_db_url: str = Field(default="sqlite:///./data/memory.db", alias="MEMORY_DB_URL")
    rag_persist_dir: str = Field(default="./data/chroma", alias="RAG_PERSIST_DIR")
    rag_collection: str = Field(default="knowledge_base", alias="RAG_COLLECTION")
    short_term_max_messages: int = Field(default=20, alias="SHORT_TERM_MAX_MESSAGES")
    agent_max_steps: int = Field(default=5, alias="AGENT_MAX_STEPS")
    rag_enabled: bool = Field(default=True, alias="RAG_ENABLED")
    use_fake_llm: bool = Field(default=False, alias="USE_FAKE_LLM")
    use_fake_rag: bool = Field(default=False, alias="USE_FAKE_RAG")
    use_ollama: bool = Field(default=False, alias="USE_OLLAMA")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    ollama_chat_model: str = Field(default="llama3.1", alias="OLLAMA_CHAT_MODEL")
    ollama_embed_model: str = Field(
        default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL"
    )


settings = Settings()
