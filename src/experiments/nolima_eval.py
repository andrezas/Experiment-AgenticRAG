import asyncio
import json
import logging
import os
import re
from pathlib import Path

from tqdm import tqdm

from src.experiments.index_nolima import index_context_to_qdrant
from src.shared.connectors.qdrant import QdrantStorage
from src.shared.factories.embedding_factory import get_embeddings
from src.shared.utils.log import Logger

Logger.configure()
logger = logging.getLogger(__name__)


def sanitize_collection_name(name: str) -> str:
    """Garante que o nome da coleção use apenas caracteres válidos no Qdrant."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return sanitized.lower()


async def run_experiment():
    logger.info("=== Iniciando Experimento NOLIMA (Mapeamento de Espaços Vetoriais) ===")

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_storage = QdrantStorage(host=qdrant_host, port=qdrant_port)
    provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    model_name = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
    embeddings = get_embeddings(provider=provider, model_name=model_name)

    base_dir = Path("resources/data/results_test/CL8K")

    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Diretório base não encontrado ou inválido: {base_dir}")
        await qdrant_storage.close()
        return

    subdirectories = [d for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    logger.info(f"Encontrados {len(subdirectories)} subdiretórios para processar.")

    for subdir in subdirectories:
        collection_name = sanitize_collection_name(subdir.name)

        json_files = list(subdir.glob("*.json"))
        logger.info(f"Encontrados {len(json_files)} arquivos JSON em '{subdir.name}'")

        for json_file in json_files:
            try:
                with Path(json_file).open(encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler o arquivo {json_file}: {e}.")
                continue

            eval_name = data.get("eval_name", "eval_default")
            results_list = data.get("results", [])

            logger.info(f"Processando {len(results_list)} testes contidos no arquivo JSON.")

            for idx, result in enumerate(tqdm(results_list, desc="Indexando Testes")):
                context_text = result.get("generated_context", "")
                character = result.get("selected_character", "unknown")

                if not context_text:
                    logger.warning(f"Teste no índice {idx} está sem 'generated_context'.")
                    continue

                test_context_id = f"{eval_name}_teste_{idx}"

                result["espaco_vetorial_nome"] = collection_name
                result["payload_filtering"] = test_context_id

                metadata = {
                    "test_idx": idx,
                    "selected_character": character,
                    "eval_name": eval_name,
                    "question": result.get("question", ""),
                }

                await index_context_to_qdrant(
                    context_text=context_text,
                    collection_name=collection_name,
                    metadata=metadata,
                    test_context_id=test_context_id,
                    qdrant_storage=qdrant_storage,
                    embeddings=embeddings,
                )

            try:
                with Path(json_file).open("w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"Erro ao salvar atualizações em {json_file}: {e}")

    logger.info(f"=== Experimento concluído! JSON atualizado em: {json_file} ===")
    await qdrant_storage.close()


if __name__ == "__main__":
    asyncio.run(run_experiment())
