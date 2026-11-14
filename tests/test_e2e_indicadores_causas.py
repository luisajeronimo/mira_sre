"""Verificações HTTP somente leitura; exigem credencial de teste da Diretoria."""

import pytest

from app.indicadores.contrato_causas import ler_catalogo_causas, ler_resultado_causas
from tests.test_e2e_indicadores_diretoria import (
    SERVICE_DESK, pedir, periodo_atual, pytestmark, sessao,  # noqa: F401
)


def test_causas_persistidas_e_catalogo(sessao):
    cliente, headers = sessao
    catalogo = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/causas-recorrencia/filtros", headers=headers)
    assert catalogo.status_code == 200
    ler_catalogo_causas(catalogo.json())
    t0, t1 = periodo_atual()
    resposta = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/causas-recorrencia", params={"t0": t0, "t1": t1}, headers=headers)
    assert resposta.status_code == 200
    resultado = ler_resultado_causas(resposta.json())
    assert (resultado.t0, resultado.t1) == (t0, t1)


def test_causas_nega_anonimo_e_recorte_invalido(sessao):
    cliente, headers = sessao
    t0, t1 = periodo_atual()
    for caminho in ("/indicadores/causas-recorrencia", "/indicadores/causas-recorrencia/filtros"):
        resposta = pedir(cliente, "GET", SERVICE_DESK + caminho, params={"t0": t0, "t1": t1})
        assert resposta.status_code == 401
    invalido = pedir(cliente, "GET", SERVICE_DESK + "/indicadores/causas-recorrencia", params={"t0": t1, "t1": t0}, headers=headers)
    assert invalido.status_code == 400
