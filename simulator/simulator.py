import os
import random
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Configuração
# ============================================================

XANO_BASE_URL = os.getenv("XANO_BASE_URL")

ATIVOS = [
    int(ativo_id.strip())
    for ativo_id in os.getenv("SIMULATOR_ATIVOS", "").split(",")
    if ativo_id.strip()
]

INTERVALO_CICLO_SEGUNDOS = int(
    os.getenv("SIMULATOR_INTERVAL_SECONDS", "420")
)

INTERVALO_ENTRE_ATIVOS_SEGUNDOS = int(
    os.getenv("SIMULATOR_INTERVAL_BETWEEN_ASSETS", "2")
)


def ler_id_ativo(nome_variavel):
    valor = os.getenv(nome_variavel, "").strip()

    if not valor:
        return None

    return int(valor)


ATIVO_CPU_ALTA = ler_id_ativo("SIMULATOR_ATIVO_CPU_ALTA")
ATIVO_MEMORIA_ALTA = ler_id_ativo("SIMULATOR_ATIVO_MEMORIA_ALTA")
ATIVO_TEMPERATURA_ALTA = ler_id_ativo(
    "SIMULATOR_ATIVO_TEMPERATURA_ALTA"
)
ATIVO_REDE_OFFLINE = ler_id_ativo(
    "SIMULATOR_ATIVO_REDE_OFFLINE"
)
ATIVO_SILENCIADO = ler_id_ativo(
    "SIMULATOR_ATIVO_SILENCIADO"
)


# ============================================================
# Telemetria normal
# ============================================================

def gerar_telemetria_normal(ativo_id):
    return {
        "ativos_referencia_id": ativo_id,
        "uso_cpu": round(random.uniform(20, 60), 2),
        "uso_memoria": round(random.uniform(30, 70), 2),
        "temperatura": round(random.uniform(35, 55), 2),
        "status_rede": "online",
        "evento_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }


# ============================================================
# Cenários especiais
# ============================================================

def aplicar_cenario_cpu_alta(payload):
    payload["uso_cpu"] = round(
        random.uniform(85, 100),
        2,
    )

    return payload


def aplicar_cenario_memoria_alta(payload):
    payload["uso_memoria"] = round(
        random.uniform(85, 100),
        2,
    )

    return payload


def aplicar_cenario_temperatura_alta(payload):
    payload["temperatura"] = round(
        random.uniform(75, 95),
        2,
    )

    return payload


def aplicar_cenario_rede_offline(payload):
    payload["status_rede"] = "offline"

    return payload


# ============================================================
# Geração do payload
# ============================================================

def gerar_telemetria(ativo_id):
    payload = gerar_telemetria_normal(ativo_id)

    cenarios = []

    if ativo_id == ATIVO_CPU_ALTA:
        aplicar_cenario_cpu_alta(payload)
        cenarios.append("CPU_ALTA")

    if ativo_id == ATIVO_MEMORIA_ALTA:
        aplicar_cenario_memoria_alta(payload)
        cenarios.append("MEMORIA_ALTA")

    if ativo_id == ATIVO_TEMPERATURA_ALTA:
        aplicar_cenario_temperatura_alta(payload)
        cenarios.append("TEMPERATURA_ALTA")

    if ativo_id == ATIVO_REDE_OFFLINE:
        aplicar_cenario_rede_offline(payload)
        cenarios.append("REDE_OFFLINE")

    if not cenarios:
        cenarios.append("NORMAL")

    return payload, cenarios


# ============================================================
# Envio para Xano
# ============================================================

def enviar_telemetria(payload):
    url = f"{XANO_BASE_URL}/telemetria_equipamentos"

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    if not response.ok:
        print(
            f"Erro HTTP {response.status_code}: "
            f"{response.text}"
        )

    response.raise_for_status()

    return response.json()


# ============================================================
# Log
# ============================================================

def imprimir_resultado(payload, cenarios, status_http="OK"):
    timestamp = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    print(
        f"[{timestamp}] "
        f"Ativo={payload['ativos_referencia_id']} | "
        f"Cenário={','.join(cenarios)} | "
        f"CPU={payload['uso_cpu']}% | "
        f"MEM={payload['uso_memoria']}% | "
        f"TEMP={payload['temperatura']}°C | "
        f"REDE={payload['status_rede']} | "
        f"HTTP={status_http}"
    )


# ============================================================
# Ciclo
# ============================================================

def executar_ciclo():
    print()
    print("=" * 80)
    print("Novo ciclo de telemetria")
    print("=" * 80)

    for ativo_id in ATIVOS:

        # ----------------------------------------------------
        # Silêncio
        # ----------------------------------------------------

        if ativo_id == ATIVO_SILENCIADO:
            print(
                f"[SILENCIADO] Ativo {ativo_id} "
                "não enviará telemetria neste ciclo."
            )

            continue

        try:
            payload, cenarios = gerar_telemetria(
                ativo_id
            )

            enviar_telemetria(payload)

            imprimir_resultado(
                payload,
                cenarios,
            )

        except requests.RequestException as erro:
            print(
                f"[ERRO] Falha HTTP no ativo "
                f"{ativo_id}: {erro}"
            )

        except Exception as erro:
            print(
                f"[ERRO] Falha inesperada no ativo "
                f"{ativo_id}: {erro}"
            )

        time.sleep(
            INTERVALO_ENTRE_ATIVOS_SEGUNDOS
        )


# ============================================================
# Validação
# ============================================================

def validar_configuracao():
    if not XANO_BASE_URL:
        raise RuntimeError(
            "XANO_BASE_URL não configurado no .env"
        )

    if not ATIVOS:
        raise RuntimeError(
            "SIMULATOR_ATIVOS não configurado no .env"
        )


# ============================================================
# Resumo inicial
# ============================================================

def imprimir_configuracao():
    print("=" * 80)
    print("MIRA - Simulator")
    print("=" * 80)

    print(f"Ativos: {ATIVOS}")
    print(f"Quantidade: {len(ATIVOS)}")

    print(
        f"Intervalo entre ciclos: "
        f"{INTERVALO_CICLO_SEGUNDOS} segundos"
    )

    print(
        f"Intervalo entre ativos: "
        f"{INTERVALO_ENTRE_ATIVOS_SEGUNDOS} segundos"
    )

    print()
    print("Cenários configurados:")

    print(
        f"CPU alta: "
        f"{ATIVO_CPU_ALTA or '-'}"
    )

    print(
        f"Memória alta: "
        f"{ATIVO_MEMORIA_ALTA or '-'}"
    )

    print(
        f"Temperatura alta: "
        f"{ATIVO_TEMPERATURA_ALTA or '-'}"
    )

    print(
        f"Rede offline: "
        f"{ATIVO_REDE_OFFLINE or '-'}"
    )

    print(
        f"Silenciado: "
        f"{ATIVO_SILENCIADO or '-'}"
    )

    print()
    print("Ctrl+C para encerrar.")
    print("=" * 80)


# ============================================================
# Execução principal
# ============================================================

def executar_simulador():
    validar_configuracao()

    imprimir_configuracao()

    while True:
        executar_ciclo()

        print()
        print(
            f"Ciclo concluído. "
            f"Aguardando "
            f"{INTERVALO_CICLO_SEGUNDOS} segundos..."
        )

        time.sleep(
            INTERVALO_CICLO_SEGUNDOS
        )


if __name__ == "__main__":
    try:
        executar_simulador()

    except KeyboardInterrupt:
        print()
        print("Simulator encerrado pelo usuário.")