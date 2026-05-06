"""
Serviço de orquestração de chat para o Assistente de IA do ERP Evol.

Coordena o pipeline RAG, o gerenciamento de sessão, a construção de prompts
e a chamada ao LLM para processar mensagens do usuário.
"""

from app.document_detector import detect_document
from app.llm_client import LLMClient
from app.models import ChatMessage, ChatResponse
from app.prompt_builder import PromptBuilder
from app.rag_service import RAGService
from app.session_store import SessionStore


class ChatService:
    """
    Orquestra o fluxo completo de uma requisição de chat.

    Args:
        rag_service: Serviço de busca semântica no banco vetorial.
        session_store: Armazenamento de histórico de sessões em memória.
        prompt_builder: Construtor de prompts para o LLM.
        llm_client: Cliente para chamadas ao modelo de linguagem.
    """

    def __init__(
        self,
        rag_service: RAGService,
        session_store: SessionStore,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
    ) -> None:
        self._rag_service = rag_service
        self._session_store = session_store
        self._prompt_builder = prompt_builder
        self._llm_client = llm_client

    async def process_message(
        self,
        session_id: str,
        user_message: str,
        client_history: list[ChatMessage],
    ) -> ChatResponse:
        """
        Processa uma mensagem do usuário e retorna a resposta do assistente.

        Fluxo:
        1. Recupera chunks relevantes via RAGService.
        2. Constrói o system prompt com os chunks recuperados.
        3. Obtém o histórico do servidor via SessionStore.
        4. Mescla histórico: usa client_history se o histórico do servidor estiver
           vazio, senão usa o do servidor.
        5. Constrói a lista de mensagens via PromptBuilder.
        6. Chama o LLM para obter a resposta.
        7. Salva a mensagem do usuário e a resposta no SessionStore.
        8. Retorna ChatResponse com a resposta e as fontes dos chunks.

        Args:
            session_id: Identificador único da sessão do usuário.
            user_message: Texto da mensagem enviada pelo usuário.
            client_history: Histórico de mensagens enviado pelo cliente (frontend).

        Returns:
            ChatResponse com a resposta gerada e as referências de fontes.

        Raises:
            RuntimeError: Se o RAGService (Qdrant 503) ou o LLMClient (502) falhar.
                          O histórico não é modificado em caso de erro.
        """
        # 1. Detectar se a query menciona um documento específico
        source_file = detect_document(user_message)

        # 2. Recuperar chunks via RAGService, filtrando por documento se detectado
        chunks = await self._rag_service.retrieve_chunks(user_message, source_file=source_file)

        # 3. Construir system prompt com os chunks recuperados
        system_prompt = self._prompt_builder.build_system_prompt(chunks, source_file=source_file)

        # 4. Obter histórico do servidor
        server_history = self._session_store.get_history(session_id)

        # 5. Mesclar histórico: usar client_history se servidor estiver vazio
        history = server_history if server_history else client_history

        # 6. Construir lista de mensagens para o LLM
        messages = self._prompt_builder.build_messages(
            system_prompt, history, user_message
        )

        # 7. Chamar o LLM (pode lançar RuntimeError do LLM)
        response_text = await self._llm_client.complete(messages)

        # 8. Salvar mensagem do usuário e resposta no SessionStore
        self._session_store.append_message(
            session_id, ChatMessage(role="user", content=user_message)
        )
        self._session_store.append_message(
            session_id, ChatMessage(role="assistant", content=response_text)
        )

        # 9. Retornar ChatResponse com fontes dos chunks
        sources = [chunk.metadata for chunk in chunks]
        return ChatResponse(response=response_text, sources=sources)
