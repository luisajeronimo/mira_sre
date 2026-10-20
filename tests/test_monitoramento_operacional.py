"""Contratos e estado da visão operacional de monitoramento."""

import asyncio

import httpx
import pytest

import app.monitoramento.state as monitoramento_module
from app.monitoramento.state import MonitoramentoState
from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido, XanoIndisponivel


BASE_URL = "https://xano.example/api:mira-service-desk"


def executar(corrotina):
    return asyncio.run(corrotina)


def executar_evento(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return executar(coletar())


def resposta_detalhe(*, telemetrias=None, transicoes=None, incidentes=None):
    return {
        "totem": {
            "id": 1,
            "nome_ativo": "Totem 01",
            "tipo": "Totem",
            "loja": {"id": 3, "nome": "Loja Centro"},
            "status_atual": "online",
        },
        "ultima_telemetria": {
            "id": 91,
            "evento_timestamp": 1780000030000,
            "uso_cpu": 12.5,
            "uso_memoria": 42.25,
            "temperatura": 31.75,
            "status_rede": "online",
        },
        "telemetrias": telemetrias
        if telemetrias is not None
        else [
            {
                "id": 91,
                "evento_timestamp": 1780000030000,
                "uso_cpu": 12.5,
                "uso_memoria": 42.25,
                "temperatura": 31.75,
                "status_rede": "online",
            }
        ],
        "transicoes_disponibilidade": transicoes
        if transicoes is not None
        else [
            {
                "id": 31,
                "status": "online",
                "detectado_em": 1780000040000,
                "heartbeat_limite_minutos": 15,
            }
        ],
        "incidentes_automaticos": incidentes
        if incidentes is not None
        else [
            {
                "id": 70,
                "titulo": "Totem sem heartbeat",
                "status": "Novo",
                "prioridade": "Urgente",
                "criado_em": 1780000015000,
                "ultima_atualizacao_em": 1780000015000,
                "categoria": {"id": 5, "nome": "Totem Offline / Sem Heartbeat"},
            }
        ],
    }


def test_cliente_mapeia_resumo_e_detalhe_operacional_limitado():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        if requisicao.url.path.endswith("/monitoramento/ativos"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 1,
                            "nome_ativo": "Totem 01",
                            "tipo": "Totem",
                            "loja": {"id": 3, "nome": "Loja Centro"},
                            "status_atual": "online",
                            "ultima_telemetria_em": 1780000030000,
                            "ultima_transicao_disponibilidade_em": 1780000040000,
                        }
                    ]
                },
            )
        return httpx.Response(200, json=resposta_detalhe())

    cliente = XanoServiceDeskCliente(
        BASE_URL, transport=httpx.MockTransport(responder)
    )

    ativos = executar(cliente.listar_ativos_monitoramento("token"))
    detalhe = executar(cliente.obter_detalhe_ativo_monitoramento("token", 1))

    assert ativos[0].loja is not None
    assert ativos[0].loja.nome == "Loja Centro"
    assert ativos[0].ultima_telemetria_em == 1780000030000
    assert detalhe.ultima_telemetria is not None
    assert detalhe.ultima_telemetria.uso_cpu == 12.5
    assert detalhe.transicoes_disponibilidade[0].detectado_em == 1780000040000
    assert detalhe.incidentes_automaticos[0].categoria.nome == "Totem Offline / Sem Heartbeat"
    assert str(requisicoes[1].url) == f"{BASE_URL}/monitoramento/ativos/1"


def test_cliente_preserva_ausencias_reais_e_rejeita_limite_excedido():
    ausente = resposta_detalhe(telemetrias=[], transicoes=[], incidentes=[])
    ausente["ultima_telemetria"] = None
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=ausente)),
    )

    detalhe = executar(cliente.obter_detalhe_ativo_monitoramento("token", 1))

    assert detalhe.ultima_telemetria is None
    assert detalhe.telemetrias == []
    assert detalhe.transicoes_disponibilidade == []
    assert detalhe.incidentes_automaticos == []

    excedente = resposta_detalhe(telemetrias=[ausente] * 11)
    cliente_excedente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=excedente)
        ),
    )
    with pytest.raises(XanoContratoInvalido, match="mais registros"):
        executar(cliente_excedente.obter_detalhe_ativo_monitoramento("token", 1))


class ClienteMonitoramentoFalso:
    def __init__(self, resultado=None, erro=None):
        self.resultado = resultado or type("Resultado", (), {})()
        self.erro = erro
        self.consultas = []

    async def obter_detalhe_ativo_monitoramento(self, token, ativo_id):
        self.consultas.append((token, ativo_id))
        if self.erro is not None:
            raise self.erro
        return self.resultado


def resultado_detalhe_para_estado():
    from app.services.service_desk import (
        AtivoMonitoramento,
        DetalheMonitoramento,
        IncidenteAutomaticoHeartbeat,
        ReferenciaCategoria,
        ReferenciaLoja,
        TelemetriaMonitoramento,
        TransicaoDisponibilidade,
    )

    return DetalheMonitoramento(
        totem=AtivoMonitoramento(
            id=1,
            nome_ativo="Totem 01",
            tipo="Totem",
            loja=ReferenciaLoja(id=3, nome="Loja Centro"),
            status_atual="online",
            ultima_telemetria_em=1780000030000,
            ultima_transicao_disponibilidade_em=1780000040000,
        ),
        ultima_telemetria=TelemetriaMonitoramento(
            id=91,
            evento_timestamp=1780000030000,
            uso_cpu=12.5,
            uso_memoria=42.25,
            temperatura=31.75,
            status_rede="online",
        ),
        telemetrias=[
            TelemetriaMonitoramento(
                id=91,
                evento_timestamp=1780000030000,
                uso_cpu=12.5,
                uso_memoria=42.25,
                temperatura=31.75,
                status_rede="online",
            )
        ],
        transicoes_disponibilidade=[
            TransicaoDisponibilidade(
                id=31,
                status="online",
                detectado_em=1780000040000,
                heartbeat_limite_minutos=15,
            )
        ],
        incidentes_automaticos=[],
    )


def novo_estado() -> MonitoramentoState:
    return MonitoramentoState(_reflex_internal_init=True)


def test_state_seleciona_totem_e_preserva_colecoes_vazias(monkeypatch):
    estado = novo_estado()
    object.__setattr__(estado, "_auth_token", "token")
    cliente = ClienteMonitoramentoFalso(resultado_detalhe_para_estado())
    monkeypatch.setattr(monitoramento_module, "criar_cliente_service_desk", lambda: cliente)

    executar_evento(MonitoramentoState.selecionar_totem, estado, 1)

    assert cliente.consultas == [("token", 1)]
    assert estado.totem_selecionado_id == 1
    assert estado.detalhe_totem["ultima_telemetria"]["uso_cpu"] == "12.5%"
    assert estado.detalhe_totem["ultima_telemetria"]["uso_memoria"] == "42.25%"
    assert estado.detalhe_totem["ultima_telemetria"]["temperatura"] == "31.75°C"
    assert estado.detalhe_totem["telemetrias"][0]["uso_cpu"] == "12.5%"
    assert estado.detalhe_totem["telemetrias"][0]["temperatura"] == "31.75°C"
    assert estado.detalhe_totem["transicoes"][0]["heartbeat_limite_minutos"] == "15 minutos"
    assert estado.detalhe_totem["incidentes"] == []


def test_state_mantem_ultimo_detalhe_valido_ao_falhar_consulta(monkeypatch):
    estado = novo_estado()
    object.__setattr__(estado, "_auth_token", "token")
    estado.detalhe_totem = {"id": 1, "nome_ativo": "Totem anterior"}
    estado.totem_selecionado_id = 1
    cliente = ClienteMonitoramentoFalso(erro=XanoIndisponivel("indisponível"))
    monkeypatch.setattr(monitoramento_module, "criar_cliente_service_desk", lambda: cliente)

    executar_evento(MonitoramentoState.selecionar_totem, estado, 2)

    assert estado.totem_selecionado_id == 1
    assert estado.detalhe_totem["nome_ativo"] == "Totem anterior"
    assert estado.mensagem_erro_detalhe
