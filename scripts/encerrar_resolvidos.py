"""Dispara uma única verificação de encerramento de chamados no Xano.

O Xano seleciona os candidatos, verifica as 72 horas e grava os efeitos.
Este comando não recebe IDs de chamados e não executa ciclos periódicos.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

import requests
from dotenv import load_dotenv


CONTAGENS = (
    "avaliados",
    "encerrados",
    "fora_vigencia",
    "prazo_nao_vencido",
    "nao_calculaveis",
    "conflitos",
)


def verificar_encerramento(
    base_url: str, chave: str, timeout: float, cliente=requests
) -> dict[str, int]:
    """Chama o endpoint uma vez e retorna apenas as contagens aprovadas."""

    if not base_url.strip():
        raise ValueError("XANO_SERVICE_DESK_BASE_URL não configurado")
    if not chave.strip():
        raise ValueError("MIRA_ENCERRAMENTO_AUTOMATION_KEY não configurada")
    if timeout <= 0:
        raise ValueError("ENCERRAMENTO_REQUEST_TIMEOUT_SECONDS deve ser maior que zero")

    resposta = cliente.post(
        f"{base_url.strip().rstrip('/')}/automacao/encerrar-resolvidos",
        headers={"X-MIRA-Encerramento-Key": chave.strip()},
        timeout=timeout,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    if not isinstance(dados, Mapping):
        raise ValueError("Resposta de encerramento inválida")

    contagens: dict[str, int] = {}
    for campo in CONTAGENS:
        valor = dados.get(campo)
        if type(valor) is not int or valor < 0:
            raise ValueError("Resposta de encerramento inválida")
        contagens[campo] = valor
    return contagens


def main() -> int:
    load_dotenv()
    try:
        timeout = float(os.getenv("ENCERRAMENTO_REQUEST_TIMEOUT_SECONDS", "30"))
        contagens = verificar_encerramento(
            os.getenv("XANO_SERVICE_DESK_BASE_URL", ""),
            os.getenv("MIRA_ENCERRAMENTO_AUTOMATION_KEY", ""),
            timeout,
        )
    except (ValueError, requests.RequestException):
        print("Falha na verificação de encerramento; confira a configuração e o Xano.")
        return 1

    print("Verificação de encerramento concluída: " + ", ".join(
        f"{campo}={contagens[campo]}" for campo in CONTAGENS
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
