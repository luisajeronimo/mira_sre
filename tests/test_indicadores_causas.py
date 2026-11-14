"""Contrato, filtros e estados de apresentação de causas e recorrência."""

import asyncio
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

import app.indicadores.state as modulo_estado
from app.indicadores.contrato_causas import ler_catalogo_causas, ler_resultado_causas
from app.indicadores.state import IndicadoresDiretoriaState
from app.states.auth import AuthState
from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido, XanoIndisponivel, XanoNaoAutenticado, XanoNaoAutorizado


T0, T1, AGORA = 1791946800000, 1792033200000, 1791999000000
INSTANTE = datetime.fromtimestamp(AGORA / 1000, ZoneInfo("America/Sao_Paulo"))


def resposta(*, loja=None, totem=None, categoria=None):
    segmento = {"id": 1, "nome": "Loja A", "elegiveis": 3, "recorrentes": 2, "percentual": 66.67}
    return {
        "periodo": {"t0": T0, "t1": T1, "observado_ate": AGORA, "fuso": "America/Sao_Paulo"},
        "filtros": {"lojas_id": loja, "ativos_referencia_id": totem, "categorias_servico_id": categoria},
        "base": {"elegiveis": 3, "cancelados": 1, "requisicoes": 2, "inconsistentes": 1, "sem_data": 2, "sem_loja": 0},
        "top_lojas": [{"id": 1, "nome": "Loja A", "quantidade": 3}],
        "pareto": {"categorias": [{"id": 2, "nome": "Falha de Rede", "quantidade": 3,
                                    "percentual": 100, "acumulado_percentual": 100, "destaque_80": True}], "categorias_80": 1},
        "recorrencia": {"janela_dias": 30, "elegiveis": 3, "recorrentes": 2, "percentual": 66.67,
                        "por_loja": [segmento], "por_totem": [segmento | {"id": 7, "nome": "Totem 7"}]},
    }


def estado():
    e = IndicadoresDiretoriaState(parent_state=AuthState(_reflex_internal_init=True), _reflex_internal_init=True)
    e.data_inicio = e.data_fim = "2026-10-14"
    e.periodo_rapido = "hoje"
    e.consulta_geracao = 1
    e._auth_token = "token-sintetico"
    return e


def test_contrato_e_apresentacao_preservam_valores_recebidos():
    e = estado()
    dados = resposta()
    # O State formata o valor publicado pelo backend, sem refazer a fórmula.
    dados["recorrencia"]["percentual"] = 66.66
    e._apresentar_causas(ler_resultado_causas(dados))
    assert e.tem_causas
    assert e.causas_recorrencia_texto == "66.66%"
    assert (e.causas_elegiveis, e.causas_recorrentes) == (3, 2)
    assert e.causas_categorias_80 == 1
    assert "2 Cancelados" not in e.causas_exclusoes_texto
    assert "Sem data e sem atribuição ao período: 2" in e.causas_exclusoes_texto
    assert e.causas_top_lojas[0]["quantidade"] == 3


def test_sem_loja_preserva_base_global_e_omite_ranking():
    d = resposta()
    d["base"]["sem_loja"] = 3
    d["top_lojas"] = []
    d["recorrencia"]["por_loja"] = []
    r = ler_resultado_causas(d)
    assert r.base["elegiveis"] == 3
    assert r.base["sem_loja"] == 3
    assert r.por_loja == []


def test_vazio_e_diferente_de_zero_recorrencia():
    d = resposta()
    d["base"].update(elegiveis=0)
    d["top_lojas"] = []
    d["pareto"] = {"categorias": [], "categorias_80": 0}
    d["recorrencia"].update(elegiveis=0, recorrentes=0, percentual=None, por_loja=[], por_totem=[])
    e = estado()
    e._apresentar_causas(ler_resultado_causas(d))
    assert e.tem_causas and e.causas_recorrencia_texto == "—"
    d = resposta()
    d["recorrencia"].update(recorrentes=0, percentual=0)
    for campo in ("por_loja", "por_totem"):
        d["recorrencia"][campo][0].update(recorrentes=0, percentual=0)
    e._apresentar_causas(ler_resultado_causas(d))
    assert e.causas_recorrencia_texto == "0.00%"


@pytest.mark.parametrize("alterar", [
    lambda d: d.update(chamados=[]),
    lambda d: d["base"].update(elegiveis=True),
    lambda d: d["base"].update(sem_loja=4),
    lambda d: d["recorrencia"].update(elegiveis=4),
    lambda d: d["recorrencia"].update(recorrentes=4),
    lambda d: d["recorrencia"].update(percentual=None),
    lambda d: d["recorrencia"].update(percentual=float("nan")),
    lambda d: d["recorrencia"].update(janela_dias=29),
    lambda d: d["recorrencia"].update(por_loja=[]),
    lambda d: d["recorrencia"]["por_totem"][0].update(recorrentes=1),
    lambda d: d["pareto"].update(categorias_80=2),
    lambda d: d["pareto"]["categorias"][0].update(quantidade=4),
    lambda d: d["pareto"]["categorias"][0].update(destaque_80="sim"),
    lambda d: d["periodo"].update(observado_ate=T0),
    lambda d: d["filtros"].update(ativos_referencia_id=-1),
    lambda d: d["top_lojas"].append(deepcopy(d["top_lojas"][0])),
])
def test_rejeita_contratos_incoerentes(alterar):
    d = resposta()
    alterar(d)
    with pytest.raises(XanoContratoInvalido):
        ler_resultado_causas(d)


def test_cliente_envia_filtros_e_consume_catalogo_proprio():
    pedidos = []

    def responder(req):
        pedidos.append(req)
        if req.url.path.endswith("/filtros"):
            return httpx.Response(200, json={"lojas": [{"id": 1, "nome": "Loja A"}], "totens": [{"id": 7, "nome": "Totem 7"}], "categorias": [{"id": 2, "nome": "Falha de Rede"}]})
        return httpx.Response(200, json=resposta(loja=1, totem=7, categoria=2))

    cliente = XanoServiceDeskCliente("https://xano.example/api:mira", transport=httpx.MockTransport(responder))
    catalogo = asyncio.run(cliente.catalogo_indicadores_causas("token-sintetico"))
    r = asyncio.run(cliente.consultar_indicadores_causas("token-sintetico", t0=T0, t1=T1, lojas_id=1, ativos_referencia_id=7, categorias_servico_id=2, visao="hoje"))
    assert catalogo.totens[0].id == 7
    assert r.ativos_referencia_id == 7
    assert dict(pedidos[1].url.params) == {"t0": str(T0), "t1": str(T1), "lojas_id": "1", "ativos_referencia_id": "7", "categorias_servico_id": "2", "visao": "hoje"}


def test_state_aplica_todos_os_recortes(monkeypatch):
    e = estado()
    e.loja_id, e.totem_id, e.categoria_id = "1", "7", "2"
    chamadas = []

    class Cliente:
        async def consultar_indicadores_causas(self, token, **filtros):
            chamadas.append(filtros)
            return ler_resultado_causas(resposta(loja=1, totem=7, categoria=2))

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    asyncio.run(e._consultar_causas(carregar_catalogo=False, geracao=1, agora=INSTANTE))
    assert e.tem_causas
    assert chamadas[0] == {"t0": T0, "t1": T1, "lojas_id": 1, "ativos_referencia_id": 7, "categorias_servico_id": 2, "visao": "hoje"}


@pytest.mark.parametrize("erro,destino", [(XanoIndisponivel, None), (XanoNaoAutenticado, "/login"), (XanoNaoAutorizado, "/inicio")])
def test_erro_e_autorizacao_sem_resultado_antigo(monkeypatch, erro, destino):
    e = estado()
    e._apresentar_causas(ler_resultado_causas(resposta()))
    e._limpar_resultado()

    class Cliente:
        async def consultar_indicadores_causas(self, *args, **kwargs):
            raise erro("falha sintética")

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    assert asyncio.run(e._consultar_causas(carregar_catalogo=False, geracao=1, agora=INSTANTE)) == destino
    assert not e.tem_causas and not e.causas_pareto and not e.causas_top_lojas


def test_resposta_de_outro_recorte_nao_e_exibida(monkeypatch):
    e = estado()
    e.loja_id = "1"

    class Cliente:
        async def consultar_indicadores_causas(self, *args, **kwargs):
            return ler_resultado_causas(resposta(loja=2))

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    asyncio.run(e._consultar_causas(carregar_catalogo=False, geracao=1, agora=INSTANTE))
    assert not e.tem_causas
    assert "incompatível" in e.mensagem_erro_causas


def test_aba_causas_preserva_filtros_e_solicita_carga():
    e = estado()
    e.loja_id, e.totem_id, e.categoria_id = "1", "7", "2"
    evento = IndicadoresDiretoriaState.selecionar_aba.fn(e, "causas")
    assert evento is not None
    assert e.aba_ativa == "causas"
    assert (e.loja_id, e.totem_id, e.categoria_id) == ("1", "7", "2")


def test_catalogo_nao_aceita_dados_brutos():
    with pytest.raises(XanoContratoInvalido):
        ler_catalogo_causas({"lojas": [], "totens": [], "categorias": [], "chamados": []})
