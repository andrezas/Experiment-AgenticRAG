import logging
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.shared.connectors.qdrant import QdrantStorage
from src.shared.factories.retriever_factory import retrieve_chunks

logger = logging.getLogger(__name__)


class NaiveRAG:
    def __init__(self, llm, qdrant_storage: QdrantStorage, embeddings):
        self.llm = llm
        self.qdrant_storage = qdrant_storage
        self.embeddings = embeddings

    async def run(self, question: str, collection_name: str, test_context_id: str) -> dict[str, Any]:
        """Executa o RAG Tradicional e retorna a resposta acompanhada dos chunks validados."""
        search_result = await retrieve_chunks(
            query=question,
            collection_name=collection_name,
            test_context_id=test_context_id,
            qdrant_storage=self.qdrant_storage,
            embeddings=self.embeddings,
        )

        # Armazena as referências completas dos chunks para validação posterior
        retrieved_chunks_refs = []
        context_chunks_texts = []

        for hit in search_result:
            context_chunks_texts.append(hit.payload.get("page_content", ""))
            retrieved_chunks_refs.append(
                {"chunk_id": hit.id, "score": hit.score, "metadata": hit.payload.get("metadata", {})}
            )

        context_serialized = "\n\n---\n\n".join(context_chunks_texts)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are an investigative research agent. "
                        "Your goal is to answer the user's question based strictly on the provided context.\n "
                        "Return only the final answer with no additional explanation."
                    ),
                ),
                ("human", "Context:\n{context}\n\nQuestion: {question}"),
            ]
        )

        chain = (
            {"context": lambda x: context_serialized, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        answer = await chain.ainvoke(question)

        return {"answer": answer, "retrieved_chunks": retrieved_chunks_refs}
