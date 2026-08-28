"""Fiscal de heartbeat e consulta de telemetria do projeto MIRA.

No modo padrão, este processo solicita ao Xano a verificação de falhas.
Também oferece uma consulta pontual de telemetria para diagnóstico. As regras
para deixar um ativo offline e criar incidentes pertencem ao Xano.
"""

import argparse
import os
import time
from datetime import datetime, timezone
from typing import Any

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

INTERVALO_EXECUCAO_SEGUNDOS = int(
    os.getenv("FISCAL_INTERVAL_SECONDS", "3")   
)

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


def resumir_resposta(dados: Any) -> str:
    """Cria um resumo legível sem presumir o formato do JSON do Xano."""

    if isinstance(dados, dict):
        for campo in (
            "resumo",
            "mensagem",
            "message",
            "resultado",
        ):
            if campo in dados:
                return str(dados[campo])

        return ", ".join(
            f"{chave}={valor}"
            for chave, valor in dados.items()
        ) or "resposta vazia"

    if isinstance(dados, list):
        return f"{len(dados)} item(ns) retornado(s)"

    return str(dados)


def formatar_timestamp(timestamp_ms: Any) -> str:
    """Formata um timestamp Unix em milissegundos usando UTC."""

    if timestamp_ms in (None, ""):
        return "-"

    try:
        data = datetime.fromtimestamp(
            float(timestamp_ms) / 1000,
            tz=timezone.utc,
        )
    except (TypeError, ValueError, OSError):
        return str(timestamp_ms)

    return data.strftime("%d/%m/%Y %H:%M:%S UTC")


# ============================================================
# Verificação de falhas
# ============================================================

def verificar_falhas() -> bool:
    """Chama o endpoint do Xano uma vez e registra o resultado."""

    url = f"{XANO_BASE_URL}/verificar-falhas"
    registrar("Iniciando GET /verificar-falhas")

    try:
        resposta = requests.get(
            url,
            timeout=TIMEOUT_REQUISICAO_SEGUNDOS,
        )
        resposta.raise_for_status()

        try:
            dados = resposta.json()
        except ValueError:
            dados = resposta.text.strip() or "resposta sem conteúdo"

        registrar(
            "Verificação concluída | "
            f"HTTP={resposta.status_code} | "
            f"Resumo={resumir_resposta(dados)}"
        )
        return True

    except requests.Timeout:
        registrar(
            "API indisponível temporariamente | "
            f"timeout após {TIMEOUT_REQUISICAO_SEGUNDOS:g}s"
        )

    except requests.RequestException as erro:
        registrar(
            "API indisponível temporariamente | "
            f"erro={erro}"
        )

    return False


def consultar_telemetria(ativo_id: int, limite: int = 100) -> bool:
    """Consulta e exibe as telemetrias mais recentes de um ativo."""

    url = f"{XANO_BASE_URL}/telemetria_equipamentos"
    parametros = {
        "ativos_referencia_id": ativo_id,
        "limit": limite,
    }
    registrar(
        "Consultando telemetria | "
        f"ativo_id={ativo_id} | limite={limite}"
    )

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=TIMEOUT_REQUISICAO_SEGUNDOS,
        )
        resposta.raise_for_status()
        dados = resposta.json()

        if not isinstance(dados, list):
            raise ValueError("a API não retornou uma lista de telemetrias")

        # O filtro local mantém o resultado correto mesmo se o endpoint do
        # Xano ignorar temporariamente os parâmetros recebidos.
        telemetrias = [
            item
            for item in dados
            if isinstance(item, dict)
            and item.get("ativos_referencia_id") == ativo_id
        ][:limite]

        registrar(f"Total retornado: {len(telemetrias)}")
        for item in telemetrias:
            status = str(item.get("status_rede", "-")).lower()
            registrar(
                f"ID={item.get('id', '-')} | "
                f"Ativo={item.get('ativos_referencia_id', '-')} | "
                f"CPU={item.get('uso_cpu', '-')}% | "
                f"Memória={item.get('uso_memoria', '-')}% | "
                f"Temperatura={item.get('temperatura', '-')}°C | "
                f"Rede={status} | "
                "Data="
                f"{formatar_timestamp(item.get('evento_timestamp'))}"
            )

        return True

    except requests.Timeout:
        registrar(
            "API indisponível temporariamente | "
            f"timeout após {TIMEOUT_REQUISICAO_SEGUNDOS:g}s"
        )
    except (requests.RequestException, ValueError) as erro:
        registrar(f"Falha ao consultar telemetria | erro={erro}")

    return False


# ============================================================
# Validação e execução
# ============================================================

def validar_configuracao() -> None:
    """Interrompe o início quando a configuração é inválida."""

    if not XANO_BASE_URL:
        raise RuntimeError("XANO_BASE_URL não configurado")

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
    parser.add_argument(
        "--telemetria",
        type=int,
        metavar="ATIVO_ID",
        help="lista a telemetria de um ativo e encerra",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=100,
        help="máximo de registros no modo --telemetria (padrão: 100)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = ler_argumentos()

    try:
        if argumentos.telemetria is not None:
            validar_configuracao()
            if argumentos.telemetria <= 0:
                raise ValueError("ATIVO_ID deve ser maior que zero")
            if argumentos.limite <= 0:
                raise ValueError("--limite deve ser maior que zero")
            if not consultar_telemetria(
                argumentos.telemetria,
                argumentos.limite,
            ):
                raise SystemExit(1)
        else:
            executar_fiscal(argumentos.executar_uma_vez)
    except KeyboardInterrupt:
        registrar("Fiscal encerrado pelo usuário")
    except (RuntimeError, ValueError) as erro:
        registrar(f"Erro de configuração: {erro}")
        raise SystemExit(1)
