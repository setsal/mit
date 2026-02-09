"""LLM factory for creating ChatOpenAI/AzureChatOpenAI instances."""

from langchain_openai import AzureChatOpenAI, ChatOpenAI

from mit.config import get_config
from mit.logging import get_logger

logger = get_logger("llm")


def get_chat_llm(temperature: float | None = None) -> ChatOpenAI | AzureChatOpenAI:
    """Get a chat LLM instance based on configuration.

    Args:
        temperature: Optional temperature override

    Returns:
        ChatOpenAI or AzureChatOpenAI instance
    """
    config = get_config()
    temp = temperature if temperature is not None else config.agent.temperature

    if config.llm_provider == "azure":
        logger.debug("Using Azure OpenAI")
        return AzureChatOpenAI(
            azure_endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            api_version=config.azure_openai.api_version,
            azure_deployment=config.azure_openai.deployment,
            temperature=temp,
        )
    else:
        logger.debug("Using OpenAI")
        kwargs = {
            "api_key": config.openai.api_key,
            "model": config.openai.model,
            "temperature": temp,
        }
        # Add base_url if specified (for custom endpoints)
        if config.openai.base_url:
            kwargs["base_url"] = config.openai.base_url
        return ChatOpenAI(**kwargs)
