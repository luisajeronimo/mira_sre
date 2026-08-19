import os
import random
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


load_dotenv()

XANO_TELEMETRIA_URL = os.getenv("XANO_TELEMETRIA_URL")

TOTEM_ID = 1
INTERVALO_SEGUNDOS = 10


def gerar_telemetria() -> dict:
    return {
        "ativos_referencia_id": TOTEM_ID,
        "uso_cpu": str(random.randint(20, 80)),
        "uso_memoria": str(random.randint(30, 90)),
        "temperatura": str(random.randint(40, 65)),
        "status_rede": "Online",
        "evento_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def enviar_telemetria(telemetria: dict) -> None:
    if not XANO_TELEMETRIA_URL:
        raise RuntimeError(
            "A variável XANO_TELEMETRIA_URL não foi configurada."
        )

    response = requests.post(
        XANO_TELEMETRIA_URL,
        json=telemetria,
        timeout=10,
    )

    response.raise_for_status()


def main() -> None:
    print(f"Simulador iniciado para TOT-{TOTEM_ID:03d}")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            telemetria = gerar_telemetria()

            try:
                enviar_telemetria(telemetria)

                print(
                    f"[OK] TOT-{TOTEM_ID:03d} | "
                    f"CPU: {telemetria['uso_cpu']}% | "
                    f"Memória: {telemetria['uso_memoria']}% | "
                    f"Temp: {telemetria['temperatura']}°C"
                )

            except requests.RequestException as error:
                print(f"[ERRO] Falha ao enviar telemetria: {error}")

            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nSimulador encerrado.")


if __name__ == "__main__":
    main()