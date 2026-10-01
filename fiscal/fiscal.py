"""Fiscal de heartbeat do projeto MIRA.

O processo apenas solicita ao Xano a verificação de falhas. As regras para
deixar um ativo offline e criar incidentes pertencem exclusivamente ao Xano.
"""

import argparse
import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Configuração
# ============================================================

XANO_BASE_URL = os.getenv(
    "XANO_BASE_URL",
    "https://x8ki-letl-twmt.n7.xano.io/api:dcGrLbR1",
).rstrip("/")

INTERVALO_EXECUCAO_SEGUNDOS = int(os.getenv("FISCAL_INTERVAL_SECONDS", "300"))

TIMEOUT_REQUISICAO_SEGUNDOS = float(
    os.getenv("FISCAL_REQUEST_TIMEOUT_SECONDS", "30")
)


# ============================================================
# Utilidades de log
# ============================================================

def horario_atual() -> str:
    """Retorna o horário local usado nos registros do Fiscal."""

    return datetime.now().astimezone().strftime(
        "%d/%m/%Y %H:%M:%S %z"
    )


def registrar(mensagem: str) -> None:
    """Exibe uma mensagem acompanhada do horário da ocorrência."""

    print(f"[{horario_atual()}] {mensagem}", flush=True)


def obter_chave_fiscal() -> str:
    """Obtém a credencial obrigatória sem registrá-la em logs."""

    chave = os.getenv("MIRA_FISCAL_AUTOMATION_KEY", "").strip()
    if not chave:
        raise RuntimeError("MIRA_FISCAL_AUTOMATION_KEY não configurada")
    return chave


# ============================================================
# Verificação de falhas
# ============================================================

def verificar_falhas() -> bool:
    """Chama o endpoint do Xano uma vez e registra o resultado."""

    chave = obter_chave_fiscal()
    url = f"{XANO_BASE_URL}/verificar-falhas"
    registrar("Iniciando GET /verificar-falhas")

    try:
        resposta = requests.get(
            url,
            headers={"X-MIRA-Fiscal-Key": chave},
            timeout=TIMEOUT_REQUISICAO_SEGUNDOS,
        )
        resposta.raise_for_status()

        registrar(
            "Verificação concluída | "
            f"HTTP={resposta.status_code}"
        )
        return True

    except requests.Timeout:
        registrar(
            "API indisponível temporariamente | "
            f"timeout após {TIMEOUT_REQUISICAO_SEGUNDOS:g}s"
        )

    except requests.RequestException:
        registrar("API indisponível temporariamente")

    return False


# ============================================================
# Validação e execução
# ============================================================

def validar_configuracao() -> None:
    """Interrompe o início quando a configuração é inválida."""

    if not XANO_BASE_URL:
        raise RuntimeError("XANO_BASE_URL não configurado")

    obter_chave_fiscal()

    if INTERVALO_EXECUCAO_SEGUNDOS <= 0:
        raise RuntimeError(
            "FISCAL_INTERVAL_SECONDS deve ser maior que zero"
        )

    if TIMEOUT_REQUISICAO_SEGUNDOS <= 0:
        raise RuntimeError(
            "FISCAL_REQUEST_TIMEOUT_SECONDS deve ser maior que zero"
        )


def executar_fiscal(executar_uma_vez: bool = False) -> None:
    """Executa uma consulta ou mantém o Fiscal em ciclos periódicos."""

    validar_configuracao()

    registrar(
        "MIRA - Fiscal iniciado | "
        f"intervalo={INTERVALO_EXECUCAO_SEGUNDOS}s | "
        f"timeout={TIMEOUT_REQUISICAO_SEGUNDOS:g}s"
    )

    while True:
        verificar_falhas()

        if executar_uma_vez:
            registrar("Execução única concluída")
            return

        registrar(
            "Próxima verificação em "
            f"{INTERVALO_EXECUCAO_SEGUNDOS}s"
        )
        time.sleep(INTERVALO_EXECUCAO_SEGUNDOS)


def ler_argumentos() -> argparse.Namespace:
    """Lê as opções informadas pelo terminal."""

    parser = argparse.ArgumentParser(
        description="Fiscal de heartbeat do projeto MIRA"
    )
    parser.add_argument(
        "--once",
        "--uma-vez",
        action="store_true",
        dest="executar_uma_vez",
        help="consulta o Xano uma vez e encerra",
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = ler_argumentos()

    try:
        executar_fiscal(argumentos.executar_uma_vez)
    except KeyboardInterrupt:
        registrar("Fiscal encerrado pelo usuário")
    except (RuntimeError, ValueError) as erro:
        registrar(f"Erro de configuração: {erro}")
        raise SystemExit(1)
