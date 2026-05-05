"""
Testes unitários para PromptBuilder.

Verifica a construção correta do system prompt e da lista de mensagens
para envio ao LLM.
"""

import pytest

from app.models import ChatMessage, RetrievedChunk, SourceReference
from app.prompt_builder import (
    NO_CONTEXT_INSTRUCTION,
    SCOPE_RESTRICTION_INSTRUCTION,
    PromptBuilder,
)


def make_chunk(content: str, filename: str = "manual.pdf", page: int = 1) -> RetrievedChunk:
    """Helper para criar um RetrievedChunk de teste."""
    return RetrievedChunk(
        content=content,
        score=0.9,
        metadata=SourceReference(filename=filename, page=page),
    )


@pytest.fixture
def builder() -> PromptBuilder:
    return PromptBuilder()


# ---------------------------------------------------------------------------
# build_system_prompt — com chunks
# ---------------------------------------------------------------------------


class TestBuildSystemPromptWithChunks:
    def test_contains_scope_restriction_instruction(self, builder: PromptBuilder) -> None:
        """O system prompt deve conter a instrução de restrição de escopo."""
        chunks = [make_chunk("Como emitir uma NF-e no Evol.")]
        prompt = builder.build_system_prompt(chunks)
        assert SCOPE_RESTRICTION_INSTRUCTION in prompt

    def test_contains_chunk_content(self, builder: PromptBuilder) -> None:
        """O conteúdo dos chunks deve estar presente no system prompt."""
        chunk_text = "Passo a passo para cadastrar um fornecedor no ERP Evol."
        chunks = [make_chunk(chunk_text)]
        prompt = builder.build_system_prompt(chunks)
        assert chunk_text in prompt

    def test_contains_all_chunks_content(self, builder: PromptBuilder) -> None:
        """Todos os chunks fornecidos devem aparecer no prompt."""
        texts = [
            "Conteúdo do primeiro trecho.",
            "Conteúdo do segundo trecho.",
            "Conteúdo do terceiro trecho.",
        ]
        chunks = [make_chunk(t, filename=f"doc{i}.pdf", page=i) for i, t in enumerate(texts, 1)]
        prompt = builder.build_system_prompt(chunks)
        for text in texts:
            assert text in prompt

    def test_chunk_header_format(self, builder: PromptBuilder) -> None:
        """O cabeçalho de cada chunk deve seguir o formato esperado."""
        chunks = [make_chunk("Conteúdo A", filename="guia.pdf", page=5)]
        prompt = builder.build_system_prompt(chunks)
        assert "--- Trecho 1 de 1 (fonte: guia.pdf, página: 5) ---" in prompt

    def test_chunk_header_without_page(self, builder: PromptBuilder) -> None:
        """Chunks sem número de página não devem incluir 'página:' no cabeçalho."""
        chunk = RetrievedChunk(
            content="Texto sem página.",
            score=0.8,
            metadata=SourceReference(filename="readme.txt"),
        )
        prompt = builder.build_system_prompt([chunk])
        assert "página:" not in prompt
        assert "fonte: readme.txt" in prompt

    def test_multiple_chunks_numbered_correctly(self, builder: PromptBuilder) -> None:
        """Múltiplos chunks devem ser numerados de 1 a N."""
        chunks = [make_chunk(f"Trecho {i}", filename="doc.pdf", page=i) for i in range(1, 4)]
        prompt = builder.build_system_prompt(chunks)
        assert "Trecho 1 de 3" in prompt
        assert "Trecho 2 de 3" in prompt
        assert "Trecho 3 de 3" in prompt

    def test_does_not_contain_no_context_instruction(self, builder: PromptBuilder) -> None:
        """Quando há chunks, a instrução de fallback NÃO deve aparecer."""
        chunks = [make_chunk("Algum conteúdo.")]
        prompt = builder.build_system_prompt(chunks)
        assert NO_CONTEXT_INSTRUCTION not in prompt


# ---------------------------------------------------------------------------
# build_system_prompt — sem chunks
# ---------------------------------------------------------------------------


class TestBuildSystemPromptWithoutChunks:
    def test_contains_scope_restriction_instruction(self, builder: PromptBuilder) -> None:
        """Mesmo sem chunks, a instrução de restrição de escopo deve estar presente."""
        prompt = builder.build_system_prompt([])
        assert SCOPE_RESTRICTION_INSTRUCTION in prompt

    def test_contains_fallback_instruction(self, builder: PromptBuilder) -> None:
        """Sem chunks, a instrução de fallback deve estar presente no prompt."""
        prompt = builder.build_system_prompt([])
        assert NO_CONTEXT_INSTRUCTION in prompt

    def test_does_not_contain_chunk_separator(self, builder: PromptBuilder) -> None:
        """Sem chunks, não deve haver separadores de trecho no prompt."""
        prompt = builder.build_system_prompt([])
        assert "--- Trecho" not in prompt


# ---------------------------------------------------------------------------
# build_messages
# ---------------------------------------------------------------------------


class TestBuildMessages:
    def test_system_prompt_is_first_element(self, builder: PromptBuilder) -> None:
        """O system prompt deve ser o primeiro elemento com role 'system'."""
        messages = builder.build_messages("Meu system prompt.", [], "Olá")
        assert messages[0] == {"role": "system", "content": "Meu system prompt."}

    def test_user_message_is_last_element(self, builder: PromptBuilder) -> None:
        """A mensagem do usuário deve ser o último elemento da lista."""
        history = [
            ChatMessage(role="user", content="Primeira pergunta"),
            ChatMessage(role="assistant", content="Primeira resposta"),
        ]
        messages = builder.build_messages("System.", history, "Segunda pergunta")
        assert messages[-1] == {"role": "user", "content": "Segunda pergunta"}

    def test_history_included_in_correct_order(self, builder: PromptBuilder) -> None:
        """O histórico deve ser incluído na ordem correta entre system e user."""
        history = [
            ChatMessage(role="user", content="Msg 1"),
            ChatMessage(role="assistant", content="Resp 1"),
            ChatMessage(role="user", content="Msg 2"),
            ChatMessage(role="assistant", content="Resp 2"),
        ]
        messages = builder.build_messages("System.", history, "Msg 3")

        # Índice 0 = system, 1..4 = histórico, 5 = user atual
        assert messages[1] == {"role": "user", "content": "Msg 1"}
        assert messages[2] == {"role": "assistant", "content": "Resp 1"}
        assert messages[3] == {"role": "user", "content": "Msg 2"}
        assert messages[4] == {"role": "assistant", "content": "Resp 2"}

    def test_total_length_with_history(self, builder: PromptBuilder) -> None:
        """O total de mensagens deve ser 1 (system) + len(history) + 1 (user)."""
        history = [
            ChatMessage(role="user", content="A"),
            ChatMessage(role="assistant", content="B"),
        ]
        messages = builder.build_messages("System.", history, "C")
        assert len(messages) == 4  # system + 2 history + user

    def test_empty_history(self, builder: PromptBuilder) -> None:
        """Com histórico vazio, deve retornar apenas system + user."""
        messages = builder.build_messages("System.", [], "Pergunta")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_history_roles_preserved(self, builder: PromptBuilder) -> None:
        """Os roles do histórico devem ser preservados exatamente."""
        history = [
            ChatMessage(role="user", content="Pergunta"),
            ChatMessage(role="assistant", content="Resposta"),
        ]
        messages = builder.build_messages("System.", history, "Nova pergunta")
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_message_format_is_dict_with_role_and_content(self, builder: PromptBuilder) -> None:
        """Cada mensagem deve ser um dict com exatamente as chaves 'role' e 'content'."""
        messages = builder.build_messages("System.", [], "Olá")
        for msg in messages:
            assert isinstance(msg, dict)
            assert set(msg.keys()) == {"role", "content"}
