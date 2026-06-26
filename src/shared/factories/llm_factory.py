from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel


def get_llm(provider: str, model_name: str, temperature: float = 0.0) -> BaseChatModel:
    """Retorna a instância do LLM baseado no provedor configurado."""
    if provider.lower() == "openai":
        return ChatOpenAI(model=model_name, temperature=temperature)
    elif provider.lower() == "anthropic":
        return ChatAnthropic(model=model_name, temperature=temperature)
    elif provider.lower() == "ollama":
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(model=model_name, temperature=temperature)
    else:
        raise ValueError(f"Provedor LLM não suportado: {provider}")
