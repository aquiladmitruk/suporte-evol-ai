"""
Testes unitários para TextChunker.

Verifica o comportamento de chunking de texto com tiktoken (cl100k_base).
"""

import pytest

from app.models import ChunkMetadata
from scripts.text_chunker import TextChunker


def make_metadata(filename: str = "doc.txt", page: int = 1, position: int = 0) -> ChunkMetadata:
    """Cria um ChunkMetadata de exemplo para uso nos testes."""
    return ChunkMetadata(filename=filename, page=page, position=position, chunk_index=0)


class TestTextChunkerInit:
    def test_valid_init(self):
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        assert chunker.chunk_size == 512
        assert chunker.chunk_overlap == 64

    def test_raises_when_overlap_equals_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            TextChunker(chunk_size=100, chunk_overlap=100)

    def test_raises_when_overlap_greater_than_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            TextChunker(chunk_size=50, chunk_overlap=100)

    def test_zero_overlap_is_valid(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=0)
        assert chunker.chunk_overlap == 0


class TestTextChunkerChunk:
    def test_empty_string_returns_empty_list(self):
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        result = chunker.chunk("", make_metadata())
        assert result == []

    def test_text_shorter_than_chunk_size_returns_single_chunk(self):
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        text = "Texto curto que cabe em um único chunk."
        result = chunker.chunk(text, make_metadata())
        assert len(result) == 1
        assert result[0].content == text

    def test_text_exactly_chunk_size_returns_single_chunk(self):
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        chunk_size = 10
        # Build a text that tokenizes to exactly chunk_size tokens
        word = "hello "
        tokens = []
        text_parts = []
        while len(tokens) < chunk_size:
            new_tokens = enc.encode(word)
            if len(tokens) + len(new_tokens) > chunk_size:
                break
            tokens.extend(new_tokens)
            text_parts.append(word)
        text = "".join(text_parts)

        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=2)
        result = chunker.chunk(text, make_metadata())
        assert len(result) == 1

    def test_text_longer_than_chunk_size_returns_multiple_chunks(self):
        chunker = TextChunker(chunk_size=10, chunk_overlap=2)
        # Generate a text that will definitely exceed 10 tokens
        text = " ".join(["palavra"] * 50)
        result = chunker.chunk(text, make_metadata())
        assert len(result) > 1

    def test_chunk_index_increments_correctly(self):
        chunker = TextChunker(chunk_size=10, chunk_overlap=2)
        text = " ".join(["palavra"] * 50)
        result = chunker.chunk(text, make_metadata())
        for i, chunk in enumerate(result):
            assert chunk.metadata.chunk_index == i

    def test_metadata_filename_preserved(self):
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        metadata = make_metadata(filename="manual.pdf", page=3, position=5)
        result = chunker.chunk("Texto de exemplo.", metadata)
        assert len(result) == 1
        assert result[0].metadata.filename == "manual.pdf"
        assert result[0].metadata.page == 3
        assert result[0].metadata.position == 5

    def test_chunk_index_in_metadata_is_overridden(self):
        """chunk_index do metadata de entrada deve ser ignorado; o correto é 0-based."""
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        # Even if we pass chunk_index=99, the output should start at 0
        metadata = ChunkMetadata(filename="doc.txt", page=1, position=0, chunk_index=99)
        result = chunker.chunk("Texto simples.", metadata)
        assert result[0].metadata.chunk_index == 0

    def test_overlap_tokens_appear_in_consecutive_chunks(self):
        """Os últimos chunk_overlap tokens do chunk N devem aparecer no início do chunk N+1."""
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")

        chunk_size = 10
        chunk_overlap = 3
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Build text with enough tokens for at least 2 full chunks
        text = " ".join(["word"] * 30)
        result = chunker.chunk(text, make_metadata())

        assert len(result) >= 2

        for i in range(len(result) - 1):
            tokens_current = enc.encode(result[i].content)
            tokens_next = enc.encode(result[i + 1].content)
            # The overlap is the min of chunk_overlap and the actual sizes,
            # since the last chunk may have fewer tokens than chunk_overlap.
            actual_overlap = min(chunk_overlap, len(tokens_current), len(tokens_next))
            # Last actual_overlap tokens of current chunk should equal
            # first actual_overlap tokens of the next chunk.
            assert tokens_current[-actual_overlap:] == tokens_next[:actual_overlap]

    def test_all_chunks_have_at_most_chunk_size_tokens(self):
        """Nenhum chunk deve exceder chunk_size tokens."""
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")

        chunk_size = 15
        chunk_overlap = 3
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        text = " ".join(["token"] * 100)
        result = chunker.chunk(text, make_metadata())

        for chunk in result:
            token_count = len(enc.encode(chunk.content))
            assert token_count <= chunk_size

    def test_whitespace_only_text_behavior(self):
        """Texto com apenas espaços pode tokenizar para 0 ou poucos tokens."""
        chunker = TextChunker(chunk_size=512, chunk_overlap=64)
        # Whitespace-only text: tiktoken may encode it to some tokens or none
        result = chunker.chunk("   ", make_metadata())
        # Either empty list or a single chunk with whitespace content — both are valid
        assert isinstance(result, list)
