"""Embeddings factory for OpenAI, Azure OpenAI, and Google Gemini."""

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from mit.config import get_config
from mit.logging import get_logger

logger = get_logger("embeddings")

_embeddings_instance = None


def get_embeddings():
    """Get the shared embeddings instance based on configuration."""
    global _embeddings_instance

    if _embeddings_instance is None:
        config = get_config()

        if config.llm_provider == "azure":
            logger.debug("Using Azure OpenAI Embeddings")
            _embeddings_instance = AzureOpenAIEmbeddings(
                azure_endpoint=config.azure_openai.endpoint,
                api_key=config.azure_openai.api_key,
                api_version=config.azure_openai.api_version,
                azure_deployment=config.azure_openai.embedding_deployment,
            )
        elif config.llm_provider == "gemini":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            logger.debug("Using Google Gemini Embeddings")
            _embeddings_instance = GoogleGenerativeAIEmbeddings(
                model=config.gemini.embedding_model,
                google_api_key=config.gemini.api_key,
            )
        else:
            logger.debug("Using OpenAI Embeddings")
            kwargs = {
                "api_key": config.openai.api_key,
                "model": config.openai.embedding_model,
            }
            # Add base_url if specified
            if config.openai.base_url:
                kwargs["base_url"] = config.openai.base_url
            _embeddings_instance = OpenAIEmbeddings(**kwargs)

    return _embeddings_instance
