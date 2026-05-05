"""
Testes de propriedade para o módulo de configuração (app/config.py).

# Feature: evol-erp-ai-assistant, Property 17: Falha na inicialização com variáveis obrigatórias ausentes
"""

import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.config import REQUIRED_VARS

# Caminho para o diretório backend (raiz do projeto Python)
BACKEND_DIR = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Estratégias
# ---------------------------------------------------------------------------

required_vars_strategy = st.frozensets(
    st.sampled_from(REQUIRED_VARS),
    min_size=1,
)


# ---------------------------------------------------------------------------
# Propriedade 17: Falha na inicialização com variáveis obrigatórias ausentes
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 17: Falha na inicialização com variáveis obrigatórias ausentes
@given(missing_vars=required_vars_strategy)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_property_17_missing_required_vars_causes_nonzero_exit(missing_vars: frozenset) -> None:
    """
    Para qualquer subconjunto não vazio de variáveis obrigatórias ausentes,
    o processo deve encerrar com código de saída diferente de zero e o log
    deve listar todas as variáveis ausentes.

    Valida: Requisito 9.2
    """
    # Monta um ambiente com todas as variáveis obrigatórias preenchidas
    # e depois remove as que devem estar ausentes
    full_env = {var: f"dummy_value_for_{var}" for var in REQUIRED_VARS}
    for var in missing_vars:
        full_env.pop(var, None)

    # Executa um subprocesso que tenta usar o módulo de configuração.
    # Acessar um atributo de settings dispara _load_settings(), que chama sys.exit(1)
    # quando variáveis obrigatórias estão ausentes.
    script = "from app.config import settings; _ = settings.QDRANT_URL"
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_DIR),
        env={**_minimal_system_env(), **full_env},
    )

    # O processo deve ter encerrado com código diferente de zero
    assert result.returncode != 0, (
        f"Esperado código de saída != 0 quando variáveis ausentes: {missing_vars}. "
        f"Código obtido: {result.returncode}. "
        f"Stderr: {result.stderr}"
    )

    # O log (stderr) deve mencionar cada variável ausente
    combined_output = result.stdout + result.stderr
    for var in missing_vars:
        assert var in combined_output, (
            f"Variável ausente '{var}' não foi mencionada no log. "
            f"Output: {combined_output!r}"
        )


def _minimal_system_env() -> dict:
    """
    Retorna um conjunto mínimo de variáveis de sistema necessárias para
    executar o Python corretamente (PATH, PYTHONPATH, etc.).
    """
    import os

    keep = {"PATH", "SYSTEMROOT", "TEMP", "TMP", "HOME", "USERPROFILE", "PYTHONPATH"}
    return {k: v for k, v in os.environ.items() if k in keep or k.startswith("PYTHON")}
