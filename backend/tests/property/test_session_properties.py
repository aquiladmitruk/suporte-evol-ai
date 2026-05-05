"""
Testes de propriedade para SessionStore usando Hypothesis.

Propriedades testadas:
  - P1: Ordenação cronológica do histórico de mensagens
  - P6: Descarte do histórico ao encerrar sessão
  - P7: Truncamento preserva a mensagem mais recente
"""

import tiktoken
from hypothesis import given, settings
from hypothesis import strategies as st

from app.models import ChatMessage
from app.session_store import SessionStore


# ---------------------------------------------------------------------------
# Estratégia para gerar ChatMessage
# ---------------------------------------------------------------------------


def chat_message_strategy():
    return st.builds(
        ChatMessage,
        role=st.sampled_from(["user", "assistant"]),
        content=st.text(min_size=1, max_size=200),
    )


# ---------------------------------------------------------------------------
# Propriedade 1: Ordenação cronológica do histórico de mensagens
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 1: Ordenação cronológica do histórico de mensagens
@given(messages=st.lists(chat_message_strategy(), min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_1_chronological_order(messages):
    """
    Valida: Requisito 1.5

    Para qualquer sequência de mensagens enviadas durante uma sessão, a ordem
    de exibição deve preservar exatamente a ordem de inserção (do mais antigo
    ao mais recente), sem inversões ou omissões.
    """
    store = SessionStore()
    session_id = "prop1-session"

    for msg in messages:
        store.append_message(session_id, msg)

    history = store.get_history(session_id)

    # Sem omissões: mesmo número de mensagens
    assert len(history) == len(messages)

    # Sem inversões: mesma ordem de inserção
    for i, (original, stored) in enumerate(zip(messages, history)):
        assert stored.role == original.role, (
            f"Posição {i}: role esperado '{original.role}', obtido '{stored.role}'"
        )
        assert stored.content == original.content, (
            f"Posição {i}: content esperado '{original.content}', obtido '{stored.content}'"
        )


# ---------------------------------------------------------------------------
# Propriedade 6: Descarte do histórico ao encerrar sessão
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 6: Descarte do histórico ao encerrar sessão
@given(
    session_id=st.uuids().map(str),
    messages=st.lists(chat_message_strategy(), min_size=1),
)
@settings(max_examples=100, deadline=None)
def test_property_6_clear_session_discards_history(session_id, messages):
    """
    Valida: Requisito 4.3

    Para qualquer sessão com histórico não vazio, após o encerramento da sessão
    (chamada a clear_session), qualquer tentativa de recuperar o histórico deve
    retornar uma lista vazia.
    """
    store = SessionStore()

    for msg in messages:
        store.append_message(session_id, msg)

    # Confirmar que há histórico antes do clear
    assert len(store.get_history(session_id)) > 0

    store.clear_session(session_id)

    # Após clear, deve retornar lista vazia
    assert store.get_history(session_id) == []


# ---------------------------------------------------------------------------
# Propriedade 7: Truncamento preserva a mensagem mais recente
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 7: Truncamento preserva a mensagem mais recente
@given(messages=st.lists(chat_message_strategy(), min_size=2, max_size=30))
@settings(max_examples=100)
def test_property_7_truncation_preserves_last_message(messages):
    """
    Valida: Requisito 4.4

    Para qualquer histórico de sessão, após o truncamento com preserve_last=True,
    a última mensagem do usuário deve estar presente no histórico resultante,
    e o número total de tokens deve ser menor ou igual ao limite configurado.
    """
    # Garantir que há pelo menos uma mensagem do usuário
    has_user_message = any(m.role == "user" for m in messages)
    if not has_user_message:
        # Substituir a última mensagem por uma de usuário para garantir a propriedade
        messages = list(messages)
        messages[-1] = ChatMessage(role="user", content=messages[-1].content)

    store = SessionStore()
    session_id = "prop7-session"

    for msg in messages:
        store.append_message(session_id, msg)

    # Encontrar a última mensagem do usuário antes do truncamento
    last_user_msg = None
    for msg in reversed(messages):
        if msg.role == "user":
            last_user_msg = msg
            break

    assert last_user_msg is not None, "Deve haver pelo menos uma mensagem do usuário"

    # Usar um limite de tokens pequeno para forçar truncamento
    max_tokens = 10

    store.truncate_to_token_limit(session_id, max_tokens=max_tokens, preserve_last=True)

    history = store.get_history(session_id)

    # A última mensagem do usuário deve estar presente no histórico resultante
    user_contents_in_history = [m.content for m in history if m.role == "user"]
    assert last_user_msg.content in user_contents_in_history, (
        f"A última mensagem do usuário '{last_user_msg.content}' não foi encontrada "
        f"no histórico após truncamento: {[m.content for m in history]}"
    )

    # O total de tokens do histórico resultante deve ser verificável
    # (pode exceder max_tokens apenas se a mensagem preservada sozinha já excede)
    encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(msg: ChatMessage) -> int:
        return len(encoding.encode(msg.role)) + len(encoding.encode(msg.content))

    total = sum(count_tokens(m) for m in history)

    # Se o histórico tem mais de uma mensagem, o total deve estar dentro do limite
    # Se tem apenas uma (a preservada), pode exceder — isso é aceitável pelo design
    if len(history) > 1:
        assert total <= max_tokens, (
            f"Total de tokens {total} excede o limite {max_tokens} "
            f"com {len(history)} mensagens no histórico"
        )
