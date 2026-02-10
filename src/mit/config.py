"""Configuration management for MIT framework."""

import os
from dataclasses import dataclass, field
from typing import Literal


LLMProvider = Literal["openai", "azure", "gemini"]


@dataclass
class OpenAIConfig:
    """OpenAI configuration."""

    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"))
    embedding_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    )
    base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "")
    )  # Optional: for custom endpoints


@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration."""

    api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    deployment: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    )
    embedding_deployment: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"
        )
    )
    api_version: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )


@dataclass
class GeminiConfig:
    """Google Gemini configuration."""

    api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    embedding_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    )


@dataclass
class ChromaDBConfig:
    """ChromaDB configuration."""

    persist_dir: str = field(
        default_factory=lambda: os.getenv("CHROMADB_PERSIST_DIR", "./data/rag/chroma_db")
    )


@dataclass
class AgentConfig:
    """Agent behavior configuration."""

    max_hops: int = 10
    default_top_k: int = 5
    temperature: float = 0.0
    log_level: str = field(
        default_factory=lambda: os.getenv("MIT_LOG_LEVEL", "INFO")
    )


@dataclass
class Config:
    """Main configuration container."""

    # LLM provider: "openai" (default), "azure", or "gemini"
    llm_provider: LLMProvider = field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "openai")
    )
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    azure_openai: AzureOpenAIConfig = field(default_factory=AzureOpenAIConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    chromadb: ChromaDBConfig = field(default_factory=ChromaDBConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)


# Global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
