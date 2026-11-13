"""E2E HTTP somente leitura dos Indicadores da Diretoria publicada no Xano."""

import os
import time
from datetime import datetime, timedelta, time as meia_noite
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest

from app.indicadores.contrato import ler_resultado


def configuracao(nome: str) -> str:
    valor = os.getenv(nome, "")
    if valor:
        return valor
    arquivo = Path(__file__).parents[1] / ".env"
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.startswith(nome + "="):
                return linha.partition("=")[2].strip()
    return ""


AUTH = configuracao("XANO_AUTH_BASE_URL").rstrip("/")
SERVICE_DESK = configuracao("XANO_SERVICE_DESK_BASE_URL").rstrip("/")
EMAIL = os.getenv("MIRA_E2E_EMAIL_DIRETORIA", "")
SENHA = os.getenv("MIRA_E2E_SENHA", "")
pytestmark = pytest.mark.skipif(
    not all((AUTH, SERVICE_DESK, EMAIL, SENHA)),
    reason="E2E da Diretoria: URLs e credenciais de teste não definidas",
)


def pedir(cliente: httpx.Client, metodo: str, url: str, **opcoes) -> httpx.Response:
    for _ in range(5):
        time.sleep(2.5)  # Limite compartilhado do plano Free.
        resposta = cliente.request(metodo, url, **opcoes)
        if resposta.status_code != 429:
            return resposta
        time.sleep(20)
    return resposta


@pytest.fixture(scope="module")
def sessao():
    with httpx.Client(timeout=30) as cliente:
        login = pedir(cliente, "POST", AUTH + "/login", json={"email": EMAIL, "senha": SENHA})
        assert login.status_code == 200
        token = login.json().get("authToken")
        assert token
        yield cliente, {"Authorization": "Bearer " + token}


def periodo_atual() -> tuple[int, int]:
    fuso = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso)
    inicio = datetime.combine(agora.date() - timedelta(days=29), meia_noite.min, fuso)
    return int(inicio.timestamp() * 1000), int(agora.timestamp() * 1000)


def test_diretoria_consulta_catalogo(sessao):
    cliente, cabecalhos = sessao
    resposta = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade/filtros", headers=cabecalhos)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert isinstance(corpo.get("lojas"), list)
    assert isinstance(corpo.get("totens"), list)


def test_diretoria_consulta_30_dias_com_contrato_valido(sessao):
    cliente, cabecalhos = sessao
    t0, t1 = periodo_atual()
    resposta = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade", params={"t0": t0, "t1": t1}, headers=cabecalhos)
    assert resposta.status_code == 200
    resultado = ler_resultado(resposta.json())
    assert (resultado.t0, resultado.t1) == (t0, t1)
    assert len(resultado.serie) == 30


def test_sessao_ausente_e_periodo_invalido_sao_rejeitados(sessao):
    cliente, cabecalhos = sessao
    t0, t1 = periodo_atual()
    anonimo = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade/filtros")
    assert anonimo.status_code == 401
    invalido = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade", params={"t0": t1, "t1": t1}, headers=cabecalhos)
    assert invalido.status_code == 400
    loja_invalida = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade", params={"t0": t0, "t1": t1, "lojas_id": 999999999}, headers=cabecalhos)
    assert loja_invalida.status_code == 400


def test_recorte_loja_e_totem_confirma_filtros(sessao):
    cliente, cabecalhos = sessao
    catalogo = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade/filtros", headers=cabecalhos)
    assert catalogo.status_code == 200
    corpo = catalogo.json()
    if not corpo["lojas"] or not corpo["totens"]:
        pytest.skip("Catálogo sem Loja ou Totem para recorte real")
    loja_id = corpo["lojas"][0]["id"]
    totem_id = corpo["totens"][0]["id"]
    t0, t1 = periodo_atual()
    resposta = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/disponibilidade-confiabilidade", params={"t0": t0, "t1": t1, "lojas_id": loja_id, "ativos_referencia_id": totem_id}, headers=cabecalhos)
    assert resposta.status_code == 200
    resultado = ler_resultado(resposta.json())
    assert (resultado.lojas_id, resultado.ativos_referencia_id) == (loja_id, totem_id)
