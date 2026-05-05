"""
TextChunker: divide texto em chunks de tamanho fixo com sobreposição configurável.

Usa tiktoken com o encoder cl100k_base para contagem de tokens.
"""

import tiktoken

from app.models import Chunk, ChunkMetadata


class TextChunker:
    """
    Divide texto em chunks de tamanho `chunk_size` tokens com sobreposição
    de `chunk_overlap` tokens entre chunks consecutivos.

    Args:
        chunk_size: Número máximo de tokens por chunk.
        chunk_overlap: Número de tokens sobrepostos entre chunks consecutivos.

    Raises:
        ValueError: Se `chunk_overlap` >= `chunk_size`.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) deve ser menor que "
                f"chunk_size ({chunk_size})"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._encoder = tiktoken.get_encoding("cl100k_base")

    def chunk(self, text: str, metadata: ChunkMetadata) -> list[Chunk]:
        """
        Divide o texto em chunks de tamanho `chunk_size` com sobreposição
        `chunk_overlap`, usando contagem de tokens via tiktoken.

        Args:
            text: Texto a ser dividido.
            metadata: Metadados de origem (filename, page, position).
                      O campo `chunk_index` será preenchido automaticamente.

        Returns:
            Lista de Chunk com metadados preenchidos. Retorna lista vazia
            para texto vazio ou texto que tokeniza para 0 tokens.
        """
        if not text:
            return []

        tokens = self._encoder.encode(text)

        if len(tokens) == 0:
            return []

        chunks: list[Chunk] = []
        step = self.chunk_size - self.chunk_overlap
        chunk_index = 0

        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            window_tokens = tokens[start:end]
            chunk_text = self._encoder.decode(window_tokens)

            chunk_metadata = ChunkMetadata(
                filename=metadata.filename,
                page=metadata.page,
                position=metadata.position,
                chunk_index=chunk_index,
            )

            chunks.append(Chunk(content=chunk_text, metadata=chunk_metadata))
            chunk_index += 1
            start += step

        return chunks
