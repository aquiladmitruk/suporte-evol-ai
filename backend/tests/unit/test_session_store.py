"""
Testes unitários para SessionStore.

Cobre: TTL expirado, sessão inexistente, clear_session e ordenação de mensagens.
"""

import time

import pytest

from app.models import ChatMessage
from app.session_store import SessionStore


def make_message(role: str = "user", content: str = "olá") -> ChatMessage:
    return ChatMessage(role=role, content=content)


# ---------------------------------------------------------------------------
# Sessão inexistente
# ---------------------------------------------------------------------------


def test_get_history_returns_empty_for_nonexistent_session():
    store = SessionStore()
    assert store.get_history("session-que-nao-existe") == []


# ---------------------------------------------------------------------------
# clear_session
# ---------------------------------------------------------------------------


def test_clear_session_makes_history_unrecoverable():
    store = SessionStore()
    session_id = "session-abc"
    store.append_message(session_id, make_message(content="mensagem 1"))
    store.append_message(session_id, make_message(content="mensagem 2"))

    assert len(store.get_history(session_id)) == 2

    store.clear_session(session_id)

    assert store.get_history(session_id) == []


def test_clear_session_on_nonexistent_session_does_not_raise():
    store = SessionStore()
    # Não deve levantar exceção
    store.clear_session("sessao-inexistente")


# ---------------------------------------------------------------------------
# TTL expirado
# ---------------------------------------------------------------------------


def test_expired_session_returns_empty_history():
    # TTL de 0 segundos: qualquer acesso após a criação já expira
    store = SessionStore(ttl_seconds=0)
    session_id = "session-ttl"
    store.append_message(session_id, make_message(content="msg"))

    # Aguarda um instante para garantir que o TTL seja ultrapassado
    time.sleep(0.01)

    assert store.get_history(session_id) == []


def test_session_within_ttl_returns_history():
    store = SessionStore(ttl_seconds=60)
    session_id = "session-valid"
    msg = make_message(content="mensagem válida")
    store.append_message(session_id, msg)

    history = store.get_history(session_id)
    assert len(history) == 1
    assert history[0].content == "mensagem válida"


# ---------------------------------------------------------------------------
# append_message — ordem de inserção
# ---------------------------------------------------------------------------


def test_append_message_preserves_insertion_order():
    store = SessionStore()
    session_id = "session-order"
    messages = [
        make_message(role="user", content="primeira"),
        make_message(role="assistant", content="segunda"),
        make_message(role="user", content="terceira"),
        make_message(role="assistant", content="quarta"),
    ]
    for msg in messages:
        store.append_message(session_id, msg)

    history = store.get_history(session_id)
    assert len(history) == len(messages)
    for i, msg in enumerate(messages):
        assert history[i].content == msg.content
        assert history[i].role == msg.role


def test_append_message_creates_new_session_if_not_exists():
    store = SessionStore()
    session_id = "nova-sessao"
    msg = make_message(content="primeira mensagem")
    store.append_message(session_id, msg)

    history = store.get_history(session_id)
    assert len(history) == 1
    assert history[0].content == "primeira mensagem"


# ---------------------------------------------------------------------------
# truncate_to_token_limit
# ---------------------------------------------------------------------------


def test_truncate_removes_oldest_messages():
    store = SessionStore()
    session_id = "session-trunc"

    # Adicionar várias mensagens
    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        store.append_message(session_id, make_message(role=role, content=f"msg {i}"))

    # Truncar para um limite muito pequeno
    store.truncate_to_token_limit(session_id, max_tokens=20, preserve_last=True)

    history = store.get_history(session_id)
    # Deve ter menos mensagens que as 10 originais
    assert len(history) < 10


def test_truncate_preserves_last_user_message():
    store = SessionStore()
    session_id = "session-preserve"

    store.append_message(session_id, make_message(role="user", content="primeira"))
    store.append_message(session_id, make_message(role="assistant", content="resposta"))
    store.append_message(session_id, make_message(role="user", content="ultima pergunta"))

    # Truncar para limite muito pequeno
    store.truncate_to_token_limit(session_id, max_tokens=5, preserve_last=True)

    history = store.get_history(session_id)
    contents = [m.content for m in history]
    assert "ultima pergunta" in contents


def test_truncate_on_nonexistent_session_does_not_raise():
    store = SessionStore()
    # Não deve levantar exceção
    store.truncate_to_token_limit("sessao-inexistente", max_tokens=100)
