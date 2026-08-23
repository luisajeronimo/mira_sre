import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


load_dotenv()

XANO_TELEMETRIA_URL = os.getenv("XANO_TELEMETRIA_URL")

ATIVO_ID = 1
LIMIT = 100


def formatar_timestamp(timestamp_ms):
    if not timestamp_ms:
        return "-"

    data = datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc,
    )

    return data.strftime("%d/%m/%Y %H:%M:%S UTC")


def buscar_telemetria(ativo_id, limit=100):
    url = f"{XANO_TELEMETRIA_URL}/telemetria_equipamentos"

    params = {
        "ativos_referencia_id": ativo_id,
        "limit": limit,
    }

    print("Consultando telemetria...")
    print("URL:", url)
    print("Parâmetros:", params)

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    print("Status HTTP:", response.status_code)

    response.raise_for_status()

    return response.json()


def main():
    telemetrias = buscar_telemetria(
        ativo_id=ATIVO_ID,
        limit=LIMIT,
    )

    print(f"\nTotal retornado: {len(telemetrias)}\n")

    for item in telemetrias:
        status = item["status_rede"].lower()

        print(
            f"ID={item['id']} | "
            f"Ativo={item['ativos_referencia_id']} | "
            f"CPU={item['uso_cpu']}% | "
            f"Memória={item['uso_memoria']}% | "
            f"Temperatura={item['temperatura']}°C | "
            f"Rede={status} | "
            f"Data={formatar_timestamp(item['evento_timestamp'])}"
        )


if __name__ == "__main__":
    main()