import os
import json
import re
import asyncio
import logging
from pathlib import Path
from tqdm import tqdm

from src.shared.connectors.qdrant import QdrantStorage
from src.experiments.index_nolima import index_context_to_qdrant
from src.shared.utils.log import Logger
from src.shared.factories.embedding_factory import get_embeddings

Logger.configure()
logger = logging.getLogger(__name__)

def sanitize_collection_name(name: str) -> str:
    """Garante que o nome da coleção use apenas caracteres válidos no Qdrant."""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return sanitized.lower()

async def run_experiment():
    logger.info("=== Iniciando Experimento NOLIMA (Mapeamento de Espaços Vetoriais) ===")

    # Configuração do cliente Qdrant (Pega do ambiente ou usa localhost)
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_storage = QdrantStorage(host=qdrant_host, port=qdrant_port)
    provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    model_name = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
    embeddings = get_embeddings(provider=provider, model_name=model_name)


    # TODO: Altere para o caminho real do seu arquivo JSON de testes
    base_dir = Path("resources/data/results_test/CL8K")

    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Diretório base não encontrado ou inválido: {base_dir}")
        await qdrant_storage.close()
        return
    
    json_files = list(base_dir.rglob("*.json"))
    logger.info(f"Encontrados {len(json_files)} arquivos JSON para processar.")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo {json_file}: {e}.")
            continue

        eval_name = data.get("eval_name", "eval_default")
        collection_name = sanitize_collection_name(eval_name)
        results_list = data.get("results", [])

        logger.info(f"Processando {len(results_list)} testes contidos no arquivo JSON.")

        # Itera sobre cada caso de teste usando tqdm para acompanhar o progresso
        for idx, result in enumerate(tqdm(results_list, desc="Indexando Testes")):
            context_text = result.get("generated_context", "")
            character = result.get("selected_character", "unknown")

            if not context_text:
                logger.warning(f"Teste no índice {idx} está sem 'generated_context'.")
                continue

            # Define o nome único e limpo para o espaço vetorial deste teste específico
            test_context_id = f"{collection_name}_teste_{idx}"

            # Injeta o identificador único de volta no objeto do teste
            result["espaco_vetorial_nome"] = collection_name
            result["payload_filtering"] = test_context_id

            # Monta um dicionário de metadados para salvar junto aos vetores
            metadata = {
                "test_idx": idx,
                "selected_character": character,
                "eval_name": collection_name,
                "question": result.get("question", "")
            }

            # Executa a indexação isolada no Qdrant
            await index_context_to_qdrant(
                context_text=context_text,
                collection_name=eval_name,
                metadata=metadata,
                test_context_id=test_context_id,
                qdrant_storage=qdrant_storage,
                embeddings=embeddings
            )

        # Sobrescreve o arquivo JSON original salvando a nova chave "espaco_vetorial_nome"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar atualizações em {json_file}: {e}")

    logger.info(f"=== Experimento concluído! JSON atualizado em: {json_file} ===")
    await qdrant_storage.close()


if __name__ == "__main__":
    asyncio.run(run_experiment())