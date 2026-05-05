"""
Testes unitários para o script de ingestão.

Verifica:
- DocumentLoader com arquivo TXT válido retorna texto e metadata corretos
- DocumentLoader com arquivo ilegível registra erro em log e continua (não lança exceção)
- Relatório final reflete corretamente contagens de sucesso e erro

Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models import ChunkMetadata
from scripts.document_loader import DocumentLoader


def _write_txt(tmp_path: Path, filename: str, content: str) -> Path:
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path


class TestDocumentLoaderTxt:
    def test_txt_returns_text_and_metadata(self, tmp_path: Path):
        content = "Conteúdo do documento de teste."
        _write_txt(tmp_path, "manual.txt", content)

        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))

        assert len(results) == 1
        text, metadata = results[0]
        assert text == content
        assert metadata.filename == "manual.txt"
        assert metadata.page is None
        assert metadata.position == 0

    def test_txt_metadata_is_chunk_metadata_instance(self, tmp_path: Path):
        _write_txt(tmp_path, "doc.txt", "Texto qualquer.")

        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))

        assert len(results) == 1
        _, metadata = results[0]
        assert isinstance(metadata, ChunkMetadata)

    def test_multiple_txt_files_all_returned(self, tmp_path: Path):
        _write_txt(tmp_path, "a.txt", "Conteúdo A")
        _write_txt(tmp_path, "b.txt", "Conteúdo B")

        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))

        assert len(results) == 2
        filenames = {metadata.filename for _, metadata in results}
        assert filenames == {"a.txt", "b.txt"}

    def test_unsupported_extension_is_skipped(self, tmp_path: Path):
        _write_txt(tmp_path, "doc.txt", "Texto válido.")
        unsupported = tmp_path / "arquivo.docx"
        unsupported.write_bytes(b"conteudo binario")

        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))

        assert len(results) == 1
        _, metadata = results[0]
        assert metadata.filename == "doc.txt"

    def test_empty_directory_returns_empty_iterator(self, tmp_path: Path):
        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))
        assert results == []


class TestDocumentLoaderUnreadable:
    def test_unreadable_txt_logs_error_and_continues(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        _write_txt(tmp_path, "valido.txt", "Conteúdo válido.")
        _write_txt(tmp_path, "ilegivel.txt", "conteúdo")

        loader = DocumentLoader()
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if self.name == "ilegivel.txt":
                raise PermissionError("Permission denied: 'ilegivel.txt'")
            return original_read_text(self, *args, **kwargs)

        with caplog.at_level(logging.ERROR, logger="scripts.document_loader"):
            with patch.object(Path, "read_text", mock_read_text):
                results = list(loader.load_directory(tmp_path))

        assert len(results) == 1
        _, metadata = results[0]
        assert metadata.filename == "valido.txt"

        error_messages = [r.message for r in caplog.records if r.levelno == logging.ERROR]
        assert any("ilegivel.txt" in msg for msg in error_messages)

    def test_unreadable_file_does_not_raise_exception(self, tmp_path: Path):
        _write_txt(tmp_path, "ilegivel.txt", "conteúdo")

        loader = DocumentLoader()
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if self.name == "ilegivel.txt":
                raise PermissionError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", mock_read_text):
            results = list(loader.load_directory(tmp_path))

        assert isinstance(results, list)
        assert len(results) == 0

    def test_invalid_pdf_logs_error_and_continues(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        bad_pdf = tmp_path / "corrompido.pdf"
        bad_pdf.write_bytes(b"nao e um pdf valido")
        _write_txt(tmp_path, "valido.txt", "Texto válido.")

        loader = DocumentLoader()

        with caplog.at_level(logging.ERROR, logger="scripts.document_loader"):
            results = list(loader.load_directory(tmp_path))

        txt_results = [r for r in results if r[1].filename == "valido.txt"]
        assert len(txt_results) == 1

        error_messages = [r.message for r in caplog.records if r.levelno == logging.ERROR]
        assert any("corrompido.pdf" in msg for msg in error_messages)


class TestIngestReport:
    def test_chunk_id_is_deterministic(self):
        from scripts.ingest import _chunk_id

        content = "Texto de exemplo para hash."
        assert _chunk_id(content) == _chunk_id(content)

    def test_chunk_id_differs_for_different_content(self):
        from scripts.ingest import _chunk_id

        assert _chunk_id("Conteúdo A") != _chunk_id("Conteúdo B")

    def test_chunk_id_is_valid_uuid_format(self):
        import uuid as uuid_module

        from scripts.ingest import _chunk_id

        chunk_id = _chunk_id("Qualquer conteúdo.")
        parsed = uuid_module.UUID(chunk_id)
        assert str(parsed) == chunk_id

    def test_document_loader_counts_match_files(self, tmp_path: Path):
        _write_txt(tmp_path, "doc1.txt", "Conteúdo 1")
        _write_txt(tmp_path, "doc2.txt", "Conteúdo 2")
        _write_txt(tmp_path, "doc3.txt", "Conteúdo 3")

        loader = DocumentLoader()
        results = list(loader.load_directory(tmp_path))

        assert len(results) == 3

    def test_error_count_reflects_unreadable_files(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        _write_txt(tmp_path, "valido1.txt", "Conteúdo 1")
        _write_txt(tmp_path, "valido2.txt", "Conteúdo 2")
        _write_txt(tmp_path, "ilegivel.txt", "conteúdo")

        loader = DocumentLoader()
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if self.name == "ilegivel.txt":
                raise PermissionError("Permission denied: 'ilegivel.txt'")
            return original_read_text(self, *args, **kwargs)

        with caplog.at_level(logging.ERROR, logger="scripts.document_loader"):
            with patch.object(Path, "read_text", mock_read_text):
                results = list(loader.load_directory(tmp_path))

        assert len(results) == 2
        error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_records) == 1
