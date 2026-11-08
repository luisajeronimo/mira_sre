"""Reflex do acompanhamento do solicitante e do histórico público de status.

Cobre as tasks 5.1–5.4 e 5.6–5.7 de `acompanhamento-solicitante-historico-status`
com cliente HTTP simulado (`httpx.MockTransport`) e States isolados. Não executa
o runtime Xano nem testes HTTP ponta a ponta.
"""

import asyncio
from pathlib import Path

import httpx
import pytest

import app.chamados.gerente.state as gerente_module
import app.chamados.solicitante.state as solicitante_module
import app.states.auth as auth_module
from app.app import app
from app.chamados.gerente.state import ChamadosGerenteState
from app.chamados.shared import MENSAGEM_HISTORICO_VAZIO, transicao_status_para_dict
from app.chamados.solicitante import ChamadosSolicitanteState
from app.services.service_desk import (
    TIPOS_EVENTO_TIMELINE,
    AutorTransicaoStatus,
    ChamadoDetalhe,
    ReferenciaAtivo,
    ReferenciaCategoria,
    TransicaoStatus,
    XanoServiceDeskCliente,
)
from app.states.auth import AuthState
from app.services.xano import (
    IdentidadeXano,
    XanoContratoInvalido,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)


BASE_URL = "https://xano.example/api:mira-service-desk"
ROOT = Path(__file__).parents[1]


LIBERACAO = "MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO"


@pytest.fixture(autouse=True)
def liberacao_ligada(monkeypatch):
    """Os cenários funcionais assumem os contratos publicados (gate K-B ligado)."""
    monkeypatch.setenv(LIBERACAO, "true")


def executar(corrotina):
    return asyncio.run(corrotina)


def item_lista(**alteracoes):
    dados = {
        "id": 102,
        "titulo": "Impressora",
        "descricao": "Sem papel",
        "status": "Resolvido",
        "prioridade": "Média",
        "origem": "manual",
        "criado_em": 1780000000000,
        "ultima_atualizacao_em": 1780000009000,
        "ativo": {"id": 3, "nome_ativo": "Totem 03"},
        "categoria": {"id": 2, "nome": "Falha de Rede"},
    }
    dados.update(alteracoes)
    return dados


def detalhe_payload(**alteracoes):
    dados = {
        "id": 101,
        "titulo": "Falha",
        "descricao": "Totem não conecta",
        "status": "Resolvido",
        "prioridade": "Alta",
        "origem": "manual",
        "criador_sistema": None,
        "criado_em": 1780000000000,
        "ultima_atualizacao_em": 1780000001000,
        "sla_horas_aplicado": 8,
        "ativo": {"id": 1, "nome_ativo": "Totem 01"},
        "categoria": {"id": 2, "nome": "Falha de Rede"},
        "solicitante": {"nome": "Ana"},
        "tecnico": None,
        "loja": {"id": 5, "nome": "Loja Centro"},
        "resumo_totem": None,
    }
    dados.update(alteracoes)
    return dados


def transicao_payload(**alteracoes):
    dados = {
        "id": 30,
        "status_anterior": "Em Atendimento",
        "status_resultante": "Resolvido",
        "criado_em": 1780000005000,
        "autor": {"nome": "Bruno", "perfil": "Técnico"},
    }
    dados.update(alteracoes)
    return dados


def cliente_com(resposta, requisicoes=None):
    def responder(requisicao: httpx.Request) -> httpx.Response:
        if requisicoes is not None:
            requisicoes.append(requisicao)
        return resposta(requisicao) if callable(resposta) else resposta

    return XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(responder))


# 5.1 — cliente e DTOs do solicitante


def test_lista_do_solicitante_usa_contrato_proprio_e_preserva_ordem():
    requisicoes = []
    cliente = cliente_com(
        httpx.Response(200, json={"items": [item_lista(), item_lista(id=101, status="Novo")]}),
        requisicoes,
    )

    itens = executar(cliente.listar_chamados_solicitante("token"))

    assert [item.id for item in itens] == [102, 101]
    assert str(requisicoes[0].url) == f"{BASE_URL}/solicitante/chamados"
    assert requisicoes[0].method == "GET"
    assert requisicoes[0].url.params == httpx.QueryParams()
    assert requisicoes[0].headers["Authorization"] == "Bearer token"


@pytest.mark.parametrize(
    "payload",
    [
        {"items": [item_lista(solicitante_id=8)]},
        {"items": [item_lista(lojas_id=5)]},
        {"items": [], "total": 0},
        {"items": "lista"},
    ],
    ids=["id-do-solicitante", "loja-bruta", "envelope-com-total", "colecao-invalida"],
)
def test_lista_do_solicitante_rejeita_contrato_incompativel(payload):
    cliente = cliente_com(httpx.Response(200, json=payload))

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_chamados_solicitante("token"))


def test_detalhe_do_solicitante_traz_somente_nomes_e_sem_telemetria():
    requisicoes = []
    cliente = cliente_com(
        httpx.Response(200, json={"chamado": detalhe_payload(tecnico={"nome": "Bruno"})}),
        requisicoes,
    )

    chamado = executar(cliente.obter_chamado_solicitante("token", 101))

    assert str(requisicoes[0].url) == f"{BASE_URL}/solicitante/chamados/101"
    assert chamado.solicitante.nome == "Ana"
    assert chamado.tecnico.nome == "Bruno"
    assert not hasattr(chamado, "resumo_totem")
    assert not hasattr(chamado.solicitante, "id")


@pytest.mark.parametrize(
    "alteracao",
    [
        {"solicitante": {"id": 8, "nome": "Ana"}},
        {"tecnico": {"id": 12, "nome": "Bruno"}},
        {"resumo_totem": {"id": 1}},
        {"ultima_telemetria": {"uso_cpu": 10}},
    ],
    ids=["solicitante-com-id", "tecnico-com-id", "resumo-totem", "telemetria"],
)
def test_detalhe_do_solicitante_rejeita_dados_alem_do_contrato(alteracao):
    cliente = cliente_com(httpx.Response(200, json={"chamado": detalhe_payload(**alteracao)}))

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.obter_chamado_solicitante("token", 101))


def test_comentarios_do_solicitante_usam_contrato_proprio():
    requisicoes = []
    comentario = {"id": 12, "conteudo": "Em análise", "criado_em": 1780000002000, "autor": {"nome": "Bruno"}}
    cliente = cliente_com(httpx.Response(200, json={"items": [comentario]}), requisicoes)

    comentarios = executar(cliente.listar_comentarios_publicos_solicitante("token", 101))

    assert [c.conteudo for c in comentarios] == ["Em análise"]
    assert str(requisicoes[0].url) == f"{BASE_URL}/solicitante/chamados/101/comentarios"


def test_comentario_do_solicitante_com_visibilidade_e_rejeitado():
    comentario = {"id": 12, "conteudo": "x", "criado_em": 1, "autor": None, "visibilidade": "interna"}
    cliente = cliente_com(httpx.Response(200, json={"items": [comentario]}))

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_comentarios_publicos_solicitante("token", 101))


@pytest.mark.parametrize(
    "status,erro",
    [(401, XanoNaoAutenticado), (403, XanoNaoAutorizado), (404, XanoNaoEncontrado), (500, XanoIndisponivel), (503, XanoIndisponivel)],
)
@pytest.mark.parametrize(
    "metodo,argumentos",
    [
        ("listar_chamados_solicitante", ()),
        ("obter_chamado_solicitante", (101,)),
        ("listar_comentarios_publicos_solicitante", (101,)),
        ("listar_historico_status_solicitante", (101,)),
        ("listar_historico_status_gerente", (101,)),
    ],
)
def test_classificacao_de_erros_dos_contratos_novos(status, erro, metodo, argumentos):
    cliente = cliente_com(httpx.Response(status, json={"message": "erro"}))

    with pytest.raises(erro):
        executar(getattr(cliente, metodo)("token", *argumentos))


def test_tipos_da_timeline_tecnica_inalterados():
    assert TIPOS_EVENTO_TIMELINE == frozenset(
        {"comentario", "atribuicao", "reatribuicao", "liberacao", "alteracao_chamado"}
    )


# 5.6 — cliente e DTO do histórico


@pytest.mark.parametrize(
    "metodo,rota",
    [
        ("listar_historico_status_gerente", "/gerente/chamados/101/historico-status"),
        ("listar_historico_status_solicitante", "/solicitante/chamados/101/historico-status"),
    ],
)
def test_historico_valido_por_jornada(metodo, rota):
    requisicoes = []
    payload = {
        "items": [
            transicao_payload(),
            transicao_payload(id=25, autor={"nome": "Sistema", "perfil": None}),
            transicao_payload(id=20, autor=None),
        ]
    }
    cliente = cliente_com(httpx.Response(200, json=payload), requisicoes)

    historico = executar(getattr(cliente, metodo)("token", 101))

    assert str(requisicoes[0].url) == BASE_URL + rota
    assert [t.id for t in historico] == [30, 25, 20]
    assert historico[0].autor == AutorTransicaoStatus(nome="Bruno", perfil="Técnico")
    assert historico[1].autor == AutorTransicaoStatus(nome="Sistema", perfil=None)
    assert historico[2].autor is None


@pytest.mark.parametrize(
    "item",
    [
        transicao_payload(alteracoes={"status": {}}),
        transicao_payload(visibilidade="interna"),
        transicao_payload(autor={"nome": "Bruno", "perfil": "Técnico", "id": 12}),
        transicao_payload(autor={"nome": "Bruno", "perfil": "tecnico_n1"}),
        transicao_payload(status_resultante="Em Atendimento"),
        transicao_payload(status_anterior=""),
        transicao_payload(criado_em=None),
    ],
    ids=["alteracoes-bruto", "visibilidade", "id-do-autor", "perfil-nao-oficial", "status-iguais", "status-vazio", "sem-data"],
)
def test_historico_rejeita_campos_extras_e_valores_invalidos(item):
    cliente = cliente_com(httpx.Response(200, json={"items": [item]}))

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_historico_status_solicitante("token", 101))


def test_historico_rejeita_envelope_com_campos_extras():
    cliente = cliente_com(httpx.Response(200, json={"items": [], "total": 0}))

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_historico_status_gerente("token", 101))


@pytest.mark.parametrize(
    "autor,esperado",
    [
        (AutorTransicaoStatus(nome="Bruno", perfil="Técnico"), "Bruno · Técnico"),
        (AutorTransicaoStatus(nome="Carla", perfil=None), "Carla"),
        (AutorTransicaoStatus(nome="Sistema", perfil=None), "Sistema"),
        (None, "Autor não informado"),
    ],
)
def test_apresentacao_do_autor_sem_inferencia(autor, esperado):
    transicao = TransicaoStatus(
        id=1,
        status_anterior="Novo",
        status_resultante="Em Atendimento",
        criado_em=1780000000000,
        autor=autor,
    )

    assert transicao_status_para_dict(transicao)["autor_texto"] == esperado


# 5.2 e 5.7 — State do solicitante


class ClienteSolicitante:
    def __init__(self, *, lista=None, detalhe=None, comentarios=None, historico=None):
        self.respostas = {
            "lista": lista if lista is not None else [],
            "detalhe": detalhe,
            "comentarios": comentarios if comentarios is not None else [],
            "historico": historico if historico is not None else [],
        }
        self.chamadas = []

    def _responder(self, chave):
        resposta = self.respostas[chave]
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    async def listar_chamados_solicitante(self, token):
        self.chamadas.append(("lista", token))
        return self._responder("lista")

    async def obter_chamado_solicitante(self, token, chamado_id):
        self.chamadas.append(("detalhe", chamado_id))
        return self._responder("detalhe")

    async def listar_comentarios_publicos_solicitante(self, token, chamado_id):
        self.chamadas.append(("comentarios", chamado_id))
        return self._responder("comentarios")

    async def listar_historico_status_solicitante(self, token, chamado_id):
        self.chamadas.append(("historico", chamado_id))
        return self._responder("historico")


def parse_detalhe(**alteracoes):
    cliente = cliente_com(httpx.Response(200, json={"chamado": detalhe_payload(**alteracoes)}))
    return executar(cliente.obter_chamado_solicitante("token", 101))


def parse_lista(*itens):
    cliente = cliente_com(httpx.Response(200, json={"items": list(itens)}))
    return executar(cliente.listar_chamados_solicitante("token"))


def parse_comentarios():
    comentario = {"id": 12, "conteudo": "Em análise", "criado_em": 1780000002000, "autor": {"nome": "Bruno"}}
    cliente = cliente_com(httpx.Response(200, json={"items": [comentario]}))
    return executar(cliente.listar_comentarios_publicos_solicitante("token", 101))


def parse_historico():
    cliente = cliente_com(httpx.Response(200, json={"items": [transicao_payload()]}))
    return executar(cliente.listar_historico_status_solicitante("token", 101))


def estado_com_sessao(*, token="", chamado_id="101"):
    """State filho de uma sessão real, como no registro de States do Reflex."""
    sessao = AuthState(_reflex_internal_init=True)
    sessao._auth_token = token
    estado = ChamadosSolicitanteState(parent_state=sessao, _reflex_internal_init=True)
    # O parâmetro dinâmico da rota é resolvido pelo State da sessão.
    object.__setattr__(sessao, "chamado_id", chamado_id)
    object.__setattr__(estado, "chamado_id", chamado_id)
    return estado


def novo_estado(monkeypatch, cliente, *, chamado_id="101"):
    estado = estado_com_sessao(token="token-de-teste", chamado_id=chamado_id)
    estado.parent_state.sessao_confirmada = True
    estado.parent_state.role = "tecnico"

    async def revalidar(_estado, perfil_esperado=None):
        assert perfil_esperado is None
        return None

    monkeypatch.setattr(ChamadosSolicitanteState, "_revalidar", revalidar)
    monkeypatch.setattr(solicitante_module, "criar_cliente_service_desk", lambda: cliente)
    return estado


def coletar(handler, estado):
    async def rodar():
        return [evento async for evento in handler.fn(estado)]

    return asyncio.run(rodar())


def test_state_lista_na_ordem_do_backend(monkeypatch):
    cliente = ClienteSolicitante(lista=parse_lista(item_lista(), item_lista(id=101, status="Novo")))
    estado = novo_estado(monkeypatch, cliente)

    coletar(ChamadosSolicitanteState.carregar_lista, estado)

    assert [c["id"] for c in estado.chamados] == [102, 101]
    assert estado.lista_carregada is True
    assert estado.mensagem_chamados == ""
    assert cliente.chamadas == [("lista", "token-de-teste")]


def test_state_lista_vazia_sem_erro(monkeypatch):
    estado = novo_estado(monkeypatch, ClienteSolicitante(lista=[]))

    coletar(ChamadosSolicitanteState.carregar_lista, estado)

    assert estado.chamados == []
    assert estado.lista_carregada is True
    assert estado.mensagem_chamados == ""


def test_state_lista_401_encerra_sessao(monkeypatch):
    estado = novo_estado(monkeypatch, ClienteSolicitante(lista=XanoNaoAutenticado("x")))

    eventos = coletar(ChamadosSolicitanteState.carregar_lista, estado)

    assert estado._auth_token == ""
    assert any("/login" in str(evento) for evento in eventos)


def test_state_detalhe_completo_com_comentarios_e_historico(monkeypatch):
    cliente = ClienteSolicitante(
        detalhe=parse_detalhe(),
        comentarios=parse_comentarios(),
        historico=parse_historico(),
    )
    estado = novo_estado(monkeypatch, cliente)

    coletar(ChamadosSolicitanteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.chamado["status"] == "Resolvido"
    assert "resumo_totem" not in estado.chamado
    assert [c["conteudo"] for c in estado.comentarios] == ["Em análise"]
    assert [t["status_resultante"] for t in estado.historico] == ["Resolvido"]
    assert [c[0] for c in cliente.chamadas] == ["detalhe", "comentarios", "historico"]


@pytest.mark.parametrize("chamado_id", ["999", "0", "abc"])
def test_state_404_e_id_invalido_tem_mesma_mensagem_sem_dados(monkeypatch, chamado_id):
    cliente = ClienteSolicitante(detalhe=XanoNaoEncontrado("Recurso não encontrado."))
    estado = novo_estado(monkeypatch, cliente, chamado_id=chamado_id)

    coletar(ChamadosSolicitanteState.carregar_detalhe, estado)

    assert estado.mensagem_detalhe == "Chamado não encontrado."
    assert estado.detalhe_carregado is False
    assert estado.chamado == {}
    assert estado.comentarios == [] and estado.historico == []
    assert all(chave == "detalhe" for chave, _ in cliente.chamadas)


def test_state_historico_vazio_sem_erro(monkeypatch):
    cliente = ClienteSolicitante(detalhe=parse_detalhe(), comentarios=[], historico=[])
    estado = novo_estado(monkeypatch, cliente)

    coletar(ChamadosSolicitanteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.historico == []
    assert estado.mensagem_historico == ""
    assert estado.carregando_historico is False


def test_state_falha_do_historico_preserva_detalhe_e_comentarios(monkeypatch):
    cliente = ClienteSolicitante(
        detalhe=parse_detalhe(),
        comentarios=parse_comentarios(),
        historico=XanoIndisponivel("x"),
    )
    estado = novo_estado(monkeypatch, cliente)

    coletar(ChamadosSolicitanteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.comentarios != []
    assert estado.historico == []
    assert estado.mensagem_historico != ""
    assert estado.mensagem_detalhe == ""


def test_state_falha_dos_comentarios_nao_impede_historico(monkeypatch):
    cliente = ClienteSolicitante(
        detalhe=parse_detalhe(),
        comentarios=XanoContratoInvalido("x"),
        historico=parse_historico(),
    )
    estado = novo_estado(monkeypatch, cliente)

    coletar(ChamadosSolicitanteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.mensagem_comentarios != ""
    assert len(estado.historico) == 1


def test_state_do_solicitante_nao_possui_eventos_de_escrita():
    fonte = (ROOT / "app/chamados/solicitante/state.py").read_text(encoding="utf-8")
    chamadas = {
        "criar_comentario",
        "salvar_tratativa",
        "alterar_responsavel",
        "assumir_chamado",
        "abrir_chamado",
        "rejeitar",
        "aceitar",
    }
    for chamada in chamadas:
        assert chamada not in fonte, chamada
    eventos = set(ChamadosSolicitanteState.event_handlers) - {"setvar"}
    assert {"carregar_lista", "carregar_detalhe"} <= eventos
    assert all(nome.startswith("carregar_") for nome in eventos), eventos


def test_paginas_do_solicitante_sem_acoes_nem_telemetria():
    fonte = (ROOT / "app/chamados/solicitante/pages.py").read_text(encoding="utf-8")
    for proibido in (
        "Detalhe do Totem",
        "cabecalho_detalhe_chamado",
        "rx.drawer",
        "resumo_totem",
        "telemetria",
        "text_area",
        "rx.button",
        "on_click",
        "on_submit",
        "rx.form",
        "timeline",
        "Rejeitar",
        "Aceitar",
        "dropdown_multisselecao",
        "painel_filtros",
    ):
        assert proibido not in fonte, proibido
    assert "secao_historico_status" in fonte
    assert "Você não possui chamados solicitados." in fonte
    assert '"/chamados/solicitados"' in fonte


def test_mensagem_de_historico_vazio_explica_cobertura_temporal():
    assert "Nenhuma transição de status registrada" in MENSAGEM_HISTORICO_VAZIO
    assert "anteriores à implantação do Save operacional" in MENSAGEM_HISTORICO_VAZIO


# 5.3 — rotas


def test_rotas_do_solicitante_registradas_antes_do_detalhe_dinamico():
    rotas = list(app._unevaluated_pages)
    lista = app._unevaluated_pages["chamados/solicitados"]
    detalhe = app._unevaluated_pages["chamados/solicitados/[chamado_id]"]

    assert lista.on_load.fn is ChamadosSolicitanteState.carregar_lista.fn
    assert detalhe.on_load.fn is ChamadosSolicitanteState.carregar_detalhe.fn
    assert rotas.index("chamados/solicitados") < rotas.index("chamados/[chamado_id]")
    assert rotas.index("chamados/solicitados/[chamado_id]") < rotas.index("chamados/[chamado_id]")


class ClienteSessao:
    def __init__(self, identidade):
        self.identidade = identidade

    async def obter_identidade(self, token):
        return self.identidade


@pytest.mark.parametrize("handler", ["carregar_lista", "carregar_detalhe"])
def test_rota_sem_sessao_redireciona_para_login_sem_consultar(monkeypatch, handler):
    cliente = ClienteSolicitante()
    monkeypatch.setattr(solicitante_module, "criar_cliente_service_desk", lambda: cliente)
    estado = estado_com_sessao(chamado_id="101")

    eventos = coletar(getattr(ChamadosSolicitanteState, handler), estado)

    assert any("/login" in str(evento) for evento in eventos)
    assert cliente.chamadas == []


@pytest.mark.parametrize("handler", ["carregar_lista", "carregar_detalhe"])
def test_rota_com_troca_pendente_redireciona_sem_consultar(monkeypatch, handler):
    cliente = ClienteSolicitante()
    monkeypatch.setattr(solicitante_module, "criar_cliente_service_desk", lambda: cliente)
    identidade = IdentidadeXano(id=8, nome="Ana", email="ana@example.test", role="gerente", lojas_id=5, deve_trocar_senha=True)
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: ClienteSessao(identidade))
    estado = estado_com_sessao(token="token-de-teste", chamado_id="101")

    eventos = coletar(getattr(ChamadosSolicitanteState, handler), estado)

    assert any("/primeiro-acesso" in str(evento) for evento in eventos)
    assert cliente.chamadas == []


@pytest.mark.parametrize("perfil", ["gerente", "tecnico", "diretoria", "administrador"])
def test_quatro_perfis_oficiais_carregam_a_lista(monkeypatch, perfil):
    cliente = ClienteSolicitante(lista=[])
    monkeypatch.setattr(solicitante_module, "criar_cliente_service_desk", lambda: cliente)
    identidade = IdentidadeXano(id=8, nome="Ana", email="ana@example.test", role=perfil, lojas_id=None)
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: ClienteSessao(identidade))
    estado = estado_com_sessao(token="token-de-teste")

    eventos = coletar(ChamadosSolicitanteState.carregar_lista, estado)

    assert not any("redirect" in str(evento).lower() for evento in eventos if evento is not None)
    assert estado.lista_carregada is True
    assert cliente.chamadas == [("lista", "token-de-teste")]


# 5.7 — histórico no detalhe do Gerente


def detalhe_gerente():
    return ChamadoDetalhe(
        id=101,
        titulo="Falha",
        descricao="Totem não conecta",
        status="Resolvido",
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=1780000001000,
        sla_horas_aplicado=8,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem 01"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        solicitante=None,
        tecnico=None,
    )


class ClienteGerente:
    def __init__(self, historico):
        self.historico = historico
        self.chamadas = []

    async def obter_chamado(self, token, chamado_id):
        self.chamadas.append("detalhe")
        return detalhe_gerente()

    async def listar_comentarios_publicos(self, token, chamado_id):
        self.chamadas.append("comentarios")
        return []

    async def listar_historico_status_gerente(self, token, chamado_id):
        self.chamadas.append("historico")
        if isinstance(self.historico, Exception):
            raise self.historico
        return self.historico


def estado_gerente(monkeypatch, cliente):
    estado = ChamadosGerenteState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token-de-teste")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "role", "gerente")
    object.__setattr__(estado, "chamado_id", "101")

    async def validar(_estado):
        return None

    monkeypatch.setattr(ChamadosGerenteState, "_validar_gerente", validar)
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    return estado


def test_detalhe_do_gerente_carrega_historico_pelo_contrato_do_gerente(monkeypatch):
    cliente = ClienteGerente(parse_historico())
    estado = estado_gerente(monkeypatch, cliente)

    coletar(ChamadosGerenteState.carregar_detalhe, estado)

    assert cliente.chamadas == ["detalhe", "comentarios", "historico"]
    assert [t["autor_texto"] for t in estado.historico] == ["Bruno · Técnico"]
    assert estado.mensagem_historico == ""


def test_historico_vazio_do_gerente_sem_erro(monkeypatch):
    estado = estado_gerente(monkeypatch, ClienteGerente([]))

    coletar(ChamadosGerenteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.historico == []
    assert estado.mensagem_historico == ""


def test_falha_do_historico_do_gerente_e_isolada(monkeypatch):
    estado = estado_gerente(monkeypatch, ClienteGerente(XanoNaoAutorizado("x")))

    coletar(ChamadosGerenteState.carregar_detalhe, estado)

    assert estado.detalhe_carregado is True
    assert estado.mensagem_detalhe == ""
    assert estado.historico == []
    assert estado.mensagem_historico != ""


def test_pagina_do_gerente_apresenta_secao_de_historico_sem_novas_acoes():
    fonte = (ROOT / "app/chamados/gerente/pages.py").read_text(encoding="utf-8")

    assert "secao_historico_status(" in fonte
    assert "ChamadosGerenteState.historico" in fonte
    assert "listar_historico_status_gerente" in (ROOT / "app/chamados/gerente/state.py").read_text(encoding="utf-8")


# 5.8 — liberação condicionada (gate K-B)


@pytest.mark.parametrize("valor", [None, "false", "", "1", "sim"])
@pytest.mark.parametrize("handler", ["carregar_lista", "carregar_detalhe"])
def test_sem_liberacao_rotas_do_solicitante_redirecionam_sem_consultar(monkeypatch, valor, handler):
    if valor is None:
        monkeypatch.delenv(LIBERACAO, raising=False)
    else:
        monkeypatch.setenv(LIBERACAO, valor)
    cliente = ClienteSolicitante(lista=[])
    estado = novo_estado(monkeypatch, cliente)

    eventos = coletar(getattr(ChamadosSolicitanteState, handler), estado)

    assert any("/inicio" in str(evento) for evento in eventos)
    assert cliente.chamadas == []


def test_sem_liberacao_detalhe_do_gerente_nao_consulta_historico(monkeypatch):
    monkeypatch.delenv(LIBERACAO, raising=False)
    cliente = ClienteGerente(parse_historico())
    estado = estado_gerente(monkeypatch, cliente)

    coletar(ChamadosGerenteState.carregar_detalhe, estado)

    assert cliente.chamadas == ["detalhe", "comentarios"]
    assert estado.detalhe_carregado is True
    assert estado.historico_habilitado is False
    assert estado.historico == [] and estado.mensagem_historico == ""


def test_pagina_do_gerente_condiciona_historico_a_liberacao():
    fonte = (ROOT / "app/chamados/gerente/pages.py").read_text(encoding="utf-8")

    assert "ChamadosGerenteState.detalhe_carregado & ChamadosGerenteState.historico_habilitado" in fonte
