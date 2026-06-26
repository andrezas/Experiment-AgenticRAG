from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings


def get_embeddings(provider: str, model_name: str) -> Embeddings:
    provider = provider.lower()

    if provider == "openai":
        return OpenAIEmbeddings(model=model_name)

    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"trust_remote_code": True, "device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    raise ValueError(f"Provedor de Embeddings não suportado: {provider}")
