"""Contratos e estado da visão operacional de monitoramento."""

import asyncio

import httpx
import pytest

import app.monitoramento.state as monitoramento_module
from app.monitoramento.state import MonitoramentoState
from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido, XanoIndisponivel, XanoConflito, XanoNaoAutenticado


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

    assert ativos[0].status_atual == "online"
    assert detalhe.totem.status_atual == "online"
    assert ativos[0].loja is not None
    assert ativos[0].loja.nome == "Loja Centro"
    assert ativos[0].ultima_telemetria_em == 1780000030000
    assert detalhe.ultima_telemetria is not None
    assert detalhe.ultima_telemetria.uso_cpu == 12.5
    assert detalhe.transicoes_disponibilidade[0].detectado_em == 1780000040000
    assert detalhe.incidentes_automaticos[0].categoria.nome == "Totem Offline / Sem Heartbeat"
    assert str(requisicoes[1].url) == f"{BASE_URL}/monitoramento/ativos/1"


@pytest.mark.parametrize("detalhe", [False, True])
def test_status_ausente_na_resposta_nao_vira_badge_sem_telemetria(detalhe):
    dados = resposta_detalhe()
    dados["totem"].pop("status_atual")
    corpo = dados if detalhe else {"items": [dados["totem"]]}
    cliente = XanoServiceDeskCliente(
        BASE_URL, transport=httpx.MockTransport(lambda _: httpx.Response(200, json=corpo))
    )
    with pytest.raises(XanoContratoInvalido, match="Estado do Totem ausente"):
        executar(cliente.obter_detalhe_ativo_monitoramento("token", 1) if detalhe
                 else cliente.listar_ativos_monitoramento("token"))


def test_detalhe_preserva_loja_historica_de_telemetria_e_disponibilidade():
    dados = resposta_detalhe()
    antiga = dict(dados["telemetrias"][0], loja={"id": 1, "nome": "Loja Origem"})
    recente = dict(dados["telemetrias"][0], id=92, evento_timestamp=1780000050000,
                   loja={"id": 3, "nome": "Loja Destino"})
    dados["telemetrias"] = [recente, antiga]
    dados["transicoes_disponibilidade"][0]["loja"] = {"id": 1, "nome": "Loja Origem"}
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=dados)),
    )

    detalhe = executar(cliente.obter_detalhe_ativo_monitoramento("token", 1))

    assert [item.loja.nome for item in detalhe.telemetrias] == ["Loja Destino", "Loja Origem"]
    assert detalhe.transicoes_disponibilidade[0].loja.nome == "Loja Origem"


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


def estado_para_retomada():
    from app.states.auth import AuthState
    estado = MonitoramentoState(parent_state=AuthState(_reflex_internal_init=True), _reflex_internal_init=True)
    estado._auth_token = "token"
    estado.role = "tecnico"
    estado.sessao_confirmada = True
    estado.totem_selecionado_id = 1
    estado.detalhe_totem = {"id": 1, "nome_ativo": "Totem 01", "loja_nome": "Loja Centro", "status_atual": "offline", "telemetria_simulada_ativa": False}
    return estado


def test_cancelar_dialogo_nao_envia_e_preserva_estado():
    estado = estado_para_retomada()
    MonitoramentoState.abrir_confirmacao_retomada.fn(estado)
    assert estado.confirmacao_retomada_id == 1
    MonitoramentoState.definir_confirmacao_retomada.fn(estado, False)
    assert estado.confirmacao_retomada_id is None
    assert executar_evento(MonitoramentoState.confirmar_retomada, estado) == []
    assert estado.detalhe_totem["status_atual"] == "offline"


def test_cliente_confirma_id_e_mapeia_conflito_sem_expor_chave():
    chamadas = []
    def responder(req):
        chamadas.append(req)
        return httpx.Response(200, json={"id": 1, "envio_autorizado": True, "status_atual": "offline"})
    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(responder))
    executar(cliente.retomar_telemetria("token", 1))
    assert chamadas[0].method == "POST"
    assert chamadas[0].url.path.endswith("/1/retomar-telemetria")
    assert "X-MIRA-Simulator-Key" not in chamadas[0].headers
    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(lambda _: httpx.Response(409, json={})))
    with pytest.raises(XanoConflito):
        executar(cliente.retomar_telemetria("token", 1))
    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"id": 2, "envio_autorizado": True, "status_atual": "offline"})))
    with pytest.raises(XanoContratoInvalido):
        executar(cliente.retomar_telemetria("token", 1))


@pytest.mark.parametrize("trocar_selecao", [False, True])
def test_retomada_unica_e_resposta_tardia(monkeypatch, trocar_selecao):
    from dataclasses import replace
    estado = estado_para_retomada()
    posts = []
    async def validar(self):
        return None
    class Cliente:
        async def retomar_telemetria(self, token, alvo):
            posts.append(alvo)
            await asyncio.sleep(0)
            if trocar_selecao:
                estado._versao_selecao += 1
                estado.totem_selecionado_id = 2
                estado.detalhe_totem = {"id": 2, "status_atual": "online"}
                estado.confirmacao_retomada_id = None
        async def listar_ativos_monitoramento(self, token):
            return []
        async def obter_detalhe_ativo_monitoramento(self, token, alvo):
            resultado = resultado_detalhe_para_estado()
            return replace(resultado, totem=replace(resultado.totem, status_atual="offline", telemetria_simulada_ativa=True))
    monkeypatch.setattr(MonitoramentoState, "_validar_acesso_monitoramento", validar)
    monkeypatch.setattr(monitoramento_module, "criar_cliente_service_desk", Cliente)
    MonitoramentoState.abrir_confirmacao_retomada.fn(estado)
    async def rodar():
        async def consumir():
            return [e async for e in MonitoramentoState.confirmar_retomada.fn(estado)]
        await asyncio.gather(consumir(), consumir())
    executar(rodar())
    assert posts == [1]
    assert not estado.retomando_telemetria
    if trocar_selecao:
        assert estado.detalhe_totem == {"id": 2, "status_atual": "online"}
        assert estado.mensagem_retomada == ""
    else:
        assert estado.detalhe_totem["status_atual"] == "offline"
        assert estado.detalhe_totem["telemetria_simulada_ativa"] is True
        assert "autorizado" in estado.mensagem_retomada


def test_controle_invalido_no_detalhe_e_negado():
    dados = resposta_detalhe()
    dados["totem"]["telemetria_simulada_ativa"] = "false"
    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(lambda _: httpx.Response(200, json=dados)))
    with pytest.raises(XanoContratoInvalido):
        executar(cliente.obter_detalhe_ativo_monitoramento("token", 1))


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


@pytest.mark.parametrize("erro", [XanoConflito("mudou"), XanoNaoAutenticado("expirou")])
def test_retomada_trata_conflito_e_expiracao_sem_online_otimista(monkeypatch, erro):
    estado = estado_para_retomada()
    async def validar(self):
        return None
    class Cliente:
        async def retomar_telemetria(self, token, alvo):
            raise erro
    monkeypatch.setattr(MonitoramentoState, "_validar_acesso_monitoramento", validar)
    monkeypatch.setattr(monitoramento_module, "criar_cliente_service_desk", Cliente)
    MonitoramentoState.abrir_confirmacao_retomada.fn(estado)
    eventos = executar_evento(MonitoramentoState.confirmar_retomada, estado)
    assert not estado.retomando_telemetria
    assert estado.confirmacao_retomada_id is None
    assert estado.detalhe_totem["status_atual"] == "offline"
    if isinstance(erro, XanoConflito):
        assert "mudou" in estado.erro_retomada
    else:
        assert eventos


@pytest.mark.parametrize("controle", [None, True])
def test_controle_ausente_ou_ja_ativo_nao_permite_retomar(controle):
    estado = estado_para_retomada()
    estado.detalhe_totem = {**estado.detalhe_totem, "telemetria_simulada_ativa": controle}
    MonitoramentoState.abrir_confirmacao_retomada.fn(estado)
    assert estado.confirmacao_retomada_id is None
