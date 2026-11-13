"""Contrato e apresentação dos indicadores executivos de chamados e SLA."""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest

import app.indicadores.state as modulo_estado
from app.indicadores.contrato_operacao import ler_catalogo_operacao, ler_resultado_operacao
from app.indicadores.state import IndicadoresDiretoriaState
from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido, XanoIndisponivel


T0 = 1791946800000
T1 = 1792033200000
AGORA = 1791999000000
STATUS = (
    "Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança",
    "Resolvido", "Solução Rejeitada", "Encerrado", "Cancelado",
)


def resposta(t0=T0, t1=T1, loja=None, categoria=None):
    return {
        "periodo": {"t0": t0, "t1": t1, "observado_ate": min(AGORA, t1), "fuso": "America/Sao_Paulo"},
        "filtros": {"lojas_id": loja, "categorias_servico_id": categoria},
        "volumetria": {"total": 3, "por_status": [
            {"status": status, "quantidade": 2 if status == "Em Atendimento" else 0}
            for status in STATUS
        ], "nao_classificados": 1},
        "conformidade": {"percentual": 80, "cumpriram": 8, "elegiveis": 10, "cancelados": 2, "nao_calculaveis": 1},
        "risco": {"calculado_em": AGORA, "normal": 1, "risco": 2, "critico": 1, "violado": 0,
                  "nao_calculaveis": 1, "status_nao_canonicos": 1},
        "chamados_filtrados": 20,
    }


def novo_estado():
    return IndicadoresDiretoriaState(_reflex_internal_init=True)


def test_catalogo_aceita_lojas_e_categorias():
    catalogo = ler_catalogo_operacao({"lojas": [{"id": 1, "nome": "Loja A"}], "categorias": [{"id": 2, "nome": "Falha de Rede"}]})
    assert catalogo.lojas[0].id == 1
    assert catalogo.categorias[0].nome == "Falha de Rede"


def test_contrato_aceita_bases_temporais_distintas():
    resultado = ler_resultado_operacao(resposta())
    assert resultado.volumetria.total == 3
    assert resultado.conformidade.percentual == 80
    assert resultado.risco.risco == 2
    assert resultado.risco.calculado_em == AGORA
    assert resultado.t1 > resultado.risco.calculado_em


@pytest.mark.parametrize("alteracao", [
    lambda dados: dados["filtros"].update(prioridade="Alta"),
    lambda dados: dados["volumetria"].update(total=4),
    lambda dados: dados["volumetria"]["por_status"].reverse(),
    lambda dados: dados["conformidade"].update(cumpriram=11),
    lambda dados: dados["conformidade"].update(percentual=None),
    lambda dados: dados["risco"].update(calculado_em=T0 - 1),
])
def test_contrato_rejeita_resposta_incoerente(alteracao):
    dados = resposta()
    alteracao(dados)
    with pytest.raises(XanoContratoInvalido):
        ler_resultado_operacao(dados)


def test_cliente_envia_loja_categoria_e_visao_sem_totem_ou_prioridade():
    requisicoes = []

    def atender(requisicao):
        requisicoes.append(requisicao)
        if requisicao.url.path.endswith("/filtros"):
            return httpx.Response(200, json={"lojas": [{"id": 1, "nome": "Loja A"}], "categorias": [{"id": 2, "nome": "Falha de Rede"}]})
        return httpx.Response(200, json=resposta(loja=1, categoria=2))

    cliente = XanoServiceDeskCliente("https://xano.example/api:mira-service-desk", transport=httpx.MockTransport(atender))
    catalogo = asyncio.run(cliente.catalogo_indicadores_operacao("token"))
    resultado = asyncio.run(cliente.consultar_indicadores_operacao(
        "token", t0=T0, t1=T1, lojas_id=1, categorias_servico_id=2, visao="hoje"
    ))
    assert catalogo.categorias[0].id == 2
    assert resultado.categorias_servico_id == 2
    assert dict(requisicoes[1].url.params) == {
        "t0": str(T0), "t1": str(T1), "lojas_id": "1", "categorias_servico_id": "2", "visao": "hoje",
    }


def test_state_apresenta_agregados_do_xano_sem_recalcular():
    estado = novo_estado()
    estado._apresentar_operacao(ler_resultado_operacao(resposta()))
    assert estado.volume_total == 3
    assert estado.volume_status[1] == {"rotulo": "Em Atendimento", "quantidade": 2}
    assert [(item["rotulo"], item["quantidade"]) for item in estado.volume_status_grafico] == [
        ("Em Atendimento", 2), ("Não classificados", 1),
    ]
    assert estado.conformidade_texto == "80.00%"
    assert estado.conformidade_progresso == "80%"
    assert estado.risco_faixas[1] == {"rotulo": "Risco · 70–90%", "quantidade": 2}
    assert estado.risco_instante_texto == "14/10/2026 14:30"
    assert estado.operacao_periodo_texto == "Período: 14/10/2026 00:00 até 14/10/2026 23:59"
    assert estado.risco_sem_dados is False


def test_agregados_sao_somente_leitura_e_state_nao_refaz_percentual():
    raiz = Path(__file__).parents[1]
    for nome in ("consultar_operacao_sla.xs", "resumir_sla_calculado.xs"):
        fonte = (raiz / "xano" / "function" / "indicadores" / nome).read_text(encoding="utf-8")
        assert not re.search(r"\bdb\.(add|edit|patch|del|bulk|transaction)\b", fonte)
    dados = resposta()
    dados["conformidade"]["percentual"] = 81
    estado = novo_estado()
    estado._apresentar_operacao(ler_resultado_operacao(dados))
    assert estado.conformidade_texto == "81.00%"


def test_state_consulta_risco_hoje_sem_aplicar_totem(monkeypatch):
    estado = novo_estado()
    estado.data_inicio = "2026-10-14"
    estado.data_fim = "2026-10-14"
    estado.periodo_rapido = "hoje"
    estado.loja_id = "1"
    estado.totem_id = "inválido"
    estado.categoria_id = "2"
    estado.consulta_geracao = 1
    object.__setattr__(estado, "_auth_token", "token")
    chamadas = []

    class Cliente:
        async def consultar_indicadores_operacao(self, token, **filtros):
            chamadas.append(filtros)
            return ler_resultado_operacao(resposta(loja=1, categoria=2))

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    instante = datetime.fromtimestamp(AGORA / 1000, ZoneInfo("America/Sao_Paulo"))
    assert asyncio.run(estado._consultar_operacao(carregar_catalogo=False, geracao=1, agora=instante)) is None
    assert estado.tem_operacao is True
    assert chamadas[0] == {"t0": T0, "t1": T1, "lojas_id": 1, "categorias_servico_id": 2, "visao": "hoje"}


def test_falha_limpa_operacao_anterior(monkeypatch):
    estado = novo_estado()
    estado._apresentar_operacao(ler_resultado_operacao(resposta()))
    estado._limpar_resultado()
    assert estado.volume_status_grafico == []
    estado.data_inicio = "2026-10-14"
    estado.data_fim = "2026-10-14"
    estado.periodo_rapido = "hoje"
    estado.consulta_geracao = 1
    object.__setattr__(estado, "_auth_token", "token")

    class Cliente:
        async def consultar_indicadores_operacao(self, *args, **kwargs):
            raise XanoIndisponivel("falha")

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    instante = datetime.fromtimestamp(AGORA / 1000, ZoneInfo("America/Sao_Paulo"))
    asyncio.run(estado._consultar_operacao(carregar_catalogo=False, geracao=1, agora=instante))
    assert estado.tem_operacao is False
    assert estado.mensagem_erro_operacao


def test_resposta_tardia_de_outro_recorte_e_descartada(monkeypatch):
    estado = novo_estado()
    estado.data_inicio = "2026-10-14"
    estado.data_fim = "2026-10-14"
    estado.periodo_rapido = "hoje"
    estado.consulta_geracao = 1
    object.__setattr__(estado, "_auth_token", "token")
    iniciou = asyncio.Event()
    liberar = asyncio.Event()

    class Cliente:
        async def consultar_indicadores_operacao(self, *args, **kwargs):
            iniciou.set()
            await liberar.wait()
            return ler_resultado_operacao(resposta())

    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", Cliente)
    instante = datetime.fromtimestamp(AGORA / 1000, ZoneInfo("America/Sao_Paulo"))

    async def executar():
        consulta = asyncio.create_task(estado._consultar_operacao(carregar_catalogo=False, geracao=1, agora=instante))
        await iniciou.wait()
        estado.consulta_geracao = 2
        liberar.set()
        await consulta

    asyncio.run(executar())
    assert estado.tem_operacao is False
