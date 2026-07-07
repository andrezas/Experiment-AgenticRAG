import logging
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from qdrant_client import models

from src.shared.connectors.qdrant import QdrantStorage
from shared.factories.retriever_factory import retrieve_chunks

logger = logging.getLogger(__name__)

class AgenticRAG:
    def __init__(self, llm, qdrant_storage: QdrantStorage, embeddings):
        self.llm = llm
        self.qdrant_storage = qdrant_storage
        self.embeddings = embeddings

    async def run(self, question: str, collection_name: str, test_context_id: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Executa o Agentic RAG com loops de busca iterativos, rastreando apenas os IDs acessados.
        """
        retrieved_chunks_refs = []
        seen_chunk_ids = set()

        async def search_context_tool(search_query: str) -> str:
            """
            Busca trechos relevantes no texto baseado em uma query de pesquisa.
            """
            search_result = await retrieve_chunks(
            query=search_query, 
            collection_name=collection_name, 
            test_context_id=test_context_id, 
            qdrant_storage=self.qdrant_storage, 
            embeddings=self.embeddings,
            exclude_ids=list(seen_chunk_ids) if seen_chunk_ids else None
        )
            
            context_texts = []
            for hit in search_result:
                if str(hit.id) not in seen_chunk_ids:
                    seen_chunk_ids.add(str(hit.id))
                    context_texts.append(hit.payload.get("page_content", ""))
                    retrieved_chunks_refs.append({
                        "chunk_id": str(hit.id),
                        "score": hit.score,
                        "metadata": hit.payload.get("metadata", {})
                    })
            if not context_texts:
                return "Nenhuma nova informação relevante foi encontrada com estes termos. Tente palavras-chave diferentes."
            
            return "\n\n---\n\n".join(context_texts)

        retrieval_tool = StructuredTool.from_function(
            coroutine=search_context_tool,
            name="buscar_no_documento",
            description="Busca trechos de informações no texto. Pode ser chamada várias vezes com termos diferentes."
        )

        tools = [retrieval_tool]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an investigative research agent. Your goal is to answer the user's question.\n"
                       "You have access to a search tool. You CAN and SHOULD use it as many times as needed, "
                       "rephrasing your queries if the previous ones didn't return the exact needle.\n"
                       "Once you are certain of the answer based on your searches, return ONLY the final answer with no additional explanation."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=False, 
            max_iterations=max_iterations,
            return_intermediate_steps=True
        )

        result = await agent_executor.ainvoke({"input": question})
        
        return {
            "answer": result["output"],
            "retrieved_chunks": retrieved_chunks_refs,
            "iterations_count": len(result.get("intermediate_steps", []))
        }