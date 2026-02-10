"""LLM factory for creating chat model instances."""

from langchain_openai import AzureChatOpenAI, ChatOpenAI

from mit.config import get_config
from mit.logging import get_logger

logger = get_logger("llm")


def extract_text(content) -> str:
    """Extract plain text from LLM response content.

    Handles both OpenAI (plain string) and Gemini (list of content blocks) formats.

    Args:
        content: response.content from any LLM provider

    Returns:
        Plain text string
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Gemini returns [{'type': 'text', 'text': '...', ...}, ...]
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def get_chat_llm(temperature: float | None = None):
    """Get a chat LLM instance based on configuration.

    Args:
        temperature: Optional temperature override

    Returns:
        ChatOpenAI, AzureChatOpenAI, or ChatGoogleGenerativeAI instance
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
    elif config.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        logger.debug("Using Google Gemini")
        return ChatGoogleGenerativeAI(
            model=config.gemini.model,
            google_api_key=config.gemini.api_key,
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
