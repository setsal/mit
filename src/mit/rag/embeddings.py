"""Azure OpenAI embeddings wrapper."""

from langchain_openai import AzureOpenAIEmbeddings

from mit.config import get_config

_embeddings_instance: AzureOpenAIEmbeddings | None = None


def get_embeddings() -> AzureOpenAIEmbeddings:
    """Get the shared embeddings instance."""
    global _embeddings_instance

    if _embeddings_instance is None:
        config = get_config()
        _embeddings_instance = AzureOpenAIEmbeddings(
            azure_endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            api_version=config.azure_openai.api_version,
            azure_deployment=config.azure_openai.embedding_deployment,
        )

    return _embeddings_instance
