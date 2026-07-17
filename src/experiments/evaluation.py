import asyncio
import json
import logging
import os
from pathlib import Path

from agentic_rag import AgenticRAG
from naive_rag import NaiveRAG
from tqdm import tqdm

from src.shared.connectors.qdrant import QdrantStorage
from src.shared.factories.embedding_factory import get_embeddings
from src.shared.factories.llm_factory import get_llm
from src.shared.utils.log import Logger

Logger.configure()
logger = logging.getLogger(__name__)


async def run_evaluation():
    logger.info("=== Iniciando Avaliação de Inferência (RAG vs AgenticRAG) ===")

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_storage = QdrantStorage(host=qdrant_host, port=qdrant_port)

    provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    model_name = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
    embeddings = get_embeddings(provider=provider, model_name=model_name)

    llm = get_llm("Ollama", "llama3.1:8b", 0)

    trad_pipeline = NaiveRAG(llm, qdrant_storage, embeddings)
    agen_pipeline = AgenticRAG(llm, qdrant_storage, embeddings)

    base_dir = Path("resources/data/results_test/CL8K")

    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Diretório base não encontrado: {base_dir}")
        await qdrant_storage.close()
        return

    subdirectories = [d for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    logger.info(f"Iniciando processamento de {len(subdirectories)} subdiretórios.")

    for subdir in tqdm(subdirectories, desc="Processando Subdiretórios"):
        json_files = list(subdir.glob("*.json"))

        for json_file in json_files:
            try:
                with Path(json_file).open(encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler o arquivo {json_file}: {e}")
                continue

            results_list = data.get("results", [])
            modified = False

            for result in results_list:
                question = result.get("question")
                collection_name = result.get("espaco_vetorial_nome")
                test_context_id = result.get("payload_filtering")

                if not all([question, collection_name, test_context_id]):
                    logger.warning(f"Teste ignorado (faltam metadados essenciais): {test_context_id}")
                    continue

                if "RAG" in result and "AgenticRAG" in result:
                    continue

                try:
                    res_trad = await trad_pipeline.run(question, collection_name, test_context_id)
                    result["RAG"] = {
                        "retrieve_chunks": res_trad.get("retrieved_chunks", []),
                        "result": res_trad.get("answer", ""),
                    }

                    res_agen = await agen_pipeline.run(question, collection_name, test_context_id)
                    result["AgenticRAG"] = {
                        "retrieve_chunks": res_agen.get("retrieved_chunks", []),
                        "result": res_agen.get("answer", ""),
                        "iterations_count": res_agen.get("iterations_count", 0),
                    }

                    modified = True

                except Exception as e:
                    logger.error(f"Erro na inferência do teste {test_context_id}: {e}")
                    continue

            if modified:
                try:
                    with Path(json_file).open("w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.debug(f"Resultados salvos com sucesso em {json_file.name}")
                except Exception as e:
                    logger.error(f"Erro ao salvar atualizações no arquivo {json_file}: {e}")

    logger.info("=== Experimento de Avaliação Concluído! ===")
    await qdrant_storage.close()


if __name__ == "__main__":
    asyncio.run(run_evaluation())
