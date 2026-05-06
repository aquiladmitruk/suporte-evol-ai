"""
Detector de documentos mencionados na query do usuário.

Mapeia termos que o usuário pode usar para referenciar documentos específicos
da base de conhecimento, permitindo filtrar a busca vetorial por source_file.
"""

import re

# Mapeamento: termo (regex, case-insensitive) → source_file exato no Qdrant
# A ordem importa: padrões mais específicos devem vir antes dos genéricos.
_DOCUMENT_PATTERNS: list[tuple[str, str]] = [
    # API Inter
    (r"\bapi\s+inter\b|\bbanco\s+inter\b|\binter\b", "Api_Inter.pdf"),

    # Sicredi — guia técnico PIX
    (r"\bsicredi\b.*\bpix\b|\bpix\b.*\bsicredi\b|\bguia.*sicredi\b|\bsicredi.*guia\b",
     "Guia_tecnico_integracoes_API_Pix_Sicredi.pdf"),

    # Sicredi — manual cobrança (boleto)
    (r"\bsicredi\b.*\bboleto\b|\bboleto\b.*\bsicredi\b|\bsicredi\b.*\bcobran[cç]a\b"
     r"|\bcobran[cç]a\b.*\bsicredi\b|\bmanual.*sicredi\b|\bsicredi.*manual\b",
     "Manual_da_API_Cobrança_Sicredi.pdf"),

    # Sicredi genérico (sem especificar boleto ou pix — retorna None para não filtrar)
    # Não adicionamos aqui para não forçar um dos dois documentos

    # Tray — imagens / screenshots
    (r"\btray\b.*\bimagem\b|\bimagem\b.*\btray\b|\bscreenshot.*tray\b|\btray.*screenshot\b",
     "imagens_tray.pdf"),

    # Tray — documentação de integração
    (r"\btray\b|\bintegra[cç][aã]o\s+tray\b|\bdocumenta[cç][aã]o\s+tray\b",
     "Documentação para Integração Tray.pdf"),
]


def detect_document(query: str) -> str | None:
    """
    Detecta se a query menciona um documento específico da base de conhecimento.

    Percorre os padrões em ordem de especificidade. Retorna o source_file do
    primeiro padrão que casar, ou None se nenhum documento for identificado.

    Args:
        query: Texto da pergunta do usuário.

    Returns:
        Nome exato do arquivo (source_file) no Qdrant, ou None.
    """
    normalized = query.lower().strip()
    for pattern, source_file in _DOCUMENT_PATTERNS:
        if re.search(pattern, normalized):
            return source_file
    return None
