"""
Gerenciamento de histórico de sessões em memória volátil com TTL automático.

O SessionStore armazena o histórico de conversas indexado por session_id,
com expiração automática baseada em TTL (Time-To-Live).
"""

import threading
import time
from dataclasses import dataclass, field

import tiktoken

from app.models import ChatMessage


@dataclass
class _SessionEntry:
    """Entrada interna de uma sessão: histórico + timestamp do último acesso."""

    history: list[ChatMessage] = field(default_factory=list)
    last_accessed: float = field(default_factory=time.monotonic)


class SessionStore:
    """
    Armazena o histórico de sessões em memória volátil com TTL automático.

    Cada sessão é identificada por um session_id (string). Ao acessar uma
    sessão, o TTL é verificado e a sessão é descartada se expirada.

    Args:
        ttl_seconds: Tempo de vida de uma sessão em segundos (padrão: 3600).
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl_seconds = ttl_seconds
        self._sessions: dict[str, _SessionEntry] = {}
        self._lock = threading.Lock()
        self._encoding = tiktoken.get_encoding("cl100k_base")

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _is_expired(self, entry: _SessionEntry) -> bool:
        """Retorna True se a sessão ultrapassou o TTL."""
        return (time.monotonic() - entry.last_accessed) > self._ttl_seconds

    def _get_entry(self, session_id: str) -> _SessionEntry | None:
        """
        Retorna a entrada da sessão se existir e não estiver expirada.
        Descarta automaticamente sessões expiradas.
        """
        entry = self._sessions.get(session_id)
        if entry is None:
            return None
        if self._is_expired(entry):
            del self._sessions[session_id]
            return None
        return entry

    def _count_tokens(self, message: ChatMessage) -> int:
        """Conta o número de tokens de uma mensagem usando cl100k_base."""
        # Formato aproximado usado pelo OpenAI: role + content + overhead
        return len(self._encoding.encode(message.role)) + len(
            self._encoding.encode(message.content)
        )

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def get_history(self, session_id: str) -> list[ChatMessage]:
        """
        Retorna o histórico de mensagens da sessão.

        Retorna lista vazia se a sessão não existir ou estiver expirada.
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if entry is None:
                return []
            return list(entry.history)

    def append_message(self, session_id: str, message: ChatMessage) -> None:
        """
        Adiciona uma mensagem ao histórico da sessão e atualiza o timestamp.

        Se a sessão não existir, cria uma nova. Se estiver expirada, descarta
        o histórico anterior e inicia uma nova sessão.
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if entry is None:
                entry = _SessionEntry()
                self._sessions[session_id] = entry
            entry.history.append(message)
            entry.last_accessed = time.monotonic()

    def clear_session(self, session_id: str) -> None:
        """
        Remove a sessão do armazenamento, tornando o histórico irrecuperável.

        Não levanta exceção se a sessão não existir.
        """
        with self._lock:
            self._sessions.pop(session_id, None)

    def truncate_to_token_limit(
        self,
        session_id: str,
        max_tokens: int,
        preserve_last: bool = True,
    ) -> None:
        """
        Remove mensagens mais antigas até que o total de tokens esteja dentro
        do limite especificado.

        Args:
            session_id: Identificador da sessão.
            max_tokens: Limite máximo de tokens permitido no histórico.
            preserve_last: Se True, a última mensagem do usuário é sempre
                           preservada, mesmo que exceda o limite sozinha.
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if entry is None or not entry.history:
                return

            history = entry.history

            # Identificar a última mensagem do usuário (para preserve_last)
            last_user_index: int | None = None
            if preserve_last:
                for i in range(len(history) - 1, -1, -1):
                    if history[i].role == "user":
                        last_user_index = i
                        break

            def total_tokens(msgs: list[ChatMessage]) -> int:
                return sum(self._count_tokens(m) for m in msgs)

            # Remover mensagens mais antigas enquanto o total exceder o limite,
            # respeitando a restrição de preserve_last.
            while total_tokens(history) > max_tokens and len(history) > 0:
                # Encontrar o índice mais antigo que pode ser removido
                removed = False
                for i in range(len(history)):
                    if preserve_last and i == last_user_index:
                        continue
                    history.pop(i)
                    # Atualizar last_user_index após remoção
                    if last_user_index is not None and i < last_user_index:
                        last_user_index -= 1
                    removed = True
                    break

                if not removed:
                    # Só resta a mensagem preservada; não é possível truncar mais
                    break

            entry.history = history
