import asyncio
import json

import httpx
import pytest

from app.services.service_desk import (
    XanoServiceDeskCliente,
    criar_cliente_service_desk,
)
from app.services.xano import (
    XanoConflito,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)


BASE_URL = "https://xano.example/api:mira-service-desk"


def executar(corrotina):
    return asyncio.run(corrotina)


def detalhe_valido(**alteracoes):
    chamado = {
        "id": 101,
        "titulo": "Falha observada",
        "descricao": "Totem não conecta",
        "status": "Novo",
        "prioridade": "Alta",
        "origem": "manual",
        "criador_sistema": None,
        "criado_em": 1780000000000,
        "sla_horas_aplicado": 2,
        "ativo": {"id": 1, "nome_ativo": "Totem 01"},
        "categoria": {"id": 2, "nome": "Falha de Rede"},
        "solicitante": {"id": 8, "nome": "Gerente"},
        "tecnico": None,
    }
    chamado.update(alteracoes)
    return {"chamado": chamado}


def test_cinco_contratos_usam_base_token_rotas_e_payload_exatos():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        caminho = requisicao.url.path
        if caminho.endswith("/gerente/ativos"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 1,
                            "nome_ativo": "Totem 01",
                            "tipo": "Totem",
                            "status_atual": "online",
                        }
                    ]
                },
            )
        if caminho.endswith("/gerente/categorias"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 2,
                            "nome": "Falha de Rede",
                            "tipo_itil": "Incidente",
                            "descricao": "Falha percebida",
                            "sla_horas": 2,
                        }
                    ]
                },
            )
        if caminho.endswith("/gerente/chamados/101"):
            return httpx.Response(200, json=detalhe_valido())
        if requisicao.method == "POST":
            return httpx.Response(201, json=detalhe_valido())
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 101,
                        "titulo": "Falha observada",
                        "status": "Novo",
                        "prioridade": "Alta",
                        "origem": "manual",
                        "criado_em": 1780000000000,
                        "ativo": {"id": 1, "nome_ativo": "Totem 01"},
                        "categoria": {"id": 2, "nome": "Falha de Rede"},
                    }
                ]
            },
        )

    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(responder),
    )
    ativos = executar(cliente.listar_ativos("token"))
    categorias = executar(cliente.listar_categorias("token"))
    chamados = executar(cliente.listar_chamados("token"))
    criado = executar(
        cliente.abrir_chamado(
            "token",
            ativos_referencia_id=1,
            categorias_servico_id=2,
            prioridade="Alta",
            titulo="Falha observada",
            descricao="Totem não conecta",
        )
    )
    detalhe = executar(cliente.obter_chamado("token", 101))

    assert ativos[0].id == 1
    assert categorias[0].sla_horas == 2
    assert chamados[0].origem == "manual"
    assert criado.tecnico is None
    assert detalhe.solicitante.id == 8
    assert [requisicao.method for requisicao in requisicoes] == [
        "GET",
        "GET",
        "GET",
        "POST",
        "GET",
    ]
    assert [str(requisicao.url) for requisicao in requisicoes] == [
        f"{BASE_URL}/gerente/ativos",
        f"{BASE_URL}/gerente/categorias",
        f"{BASE_URL}/gerente/chamados",
        f"{BASE_URL}/gerente/chamados",
        f"{BASE_URL}/gerente/chamados/101",
    ]
    assert all(
        requisicao.headers["Authorization"] == "Bearer token"
        for requisicao in requisicoes
    )
    assert json.loads(requisicoes[3].read()) == {
        "ativos_referencia_id": 1,
        "categorias_servico_id": 2,
        "prioridade": "Alta",
        "titulo": "Falha observada",
        "descricao": "Totem não conecta",
    }


def test_colecoes_vazias_e_nulos_legados_sao_aceitos():
    respostas = iter(
        [
            httpx.Response(200, json={"items": []}),
            httpx.Response(200, json={"items": []}),
            httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 16,
                            "titulo": "Legado",
                            "status": "Novo",
                            "prioridade": "Urgente",
                            "origem": None,
                            "criado_em": None,
                            "ativo": {"id": 1, "nome_ativo": "Totem 01"},
                            "categoria": {
                                "id": 1,
                                "nome": "Totem Offline / Sem Heartbeat",
                            },
                        }
                    ]
                },
            ),
            httpx.Response(
                200,
                json=detalhe_valido(
                    descricao=None,
                    origem=None,
                    criado_em=None,
                    sla_horas_aplicado=None,
                    solicitante=None,
                ),
            ),
        ]
    )
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(lambda _: next(respostas)),
    )

    assert executar(cliente.listar_ativos("token")) == []
    assert executar(cliente.listar_categorias("token")) == []
    assert executar(cliente.listar_chamados("token"))[0].origem is None
    detalhe = executar(cliente.obter_chamado("token", 16))
    assert detalhe.descricao is None
    assert detalhe.sla_horas_aplicado is None
    assert detalhe.solicitante is None
    assert detalhe.criador_sistema is None


def test_detalhe_automatico_expoe_criador_sistema_sem_solicitante_humano():
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json=detalhe_valido(
                    origem="automatico",
                    criador_sistema="bot_fiscalizacao",
                    solicitante=None,
                ),
            )
        ),
    )

    detalhe = executar(cliente.obter_chamado("token", 101))

    assert detalhe.origem == "automatico"
    assert detalhe.solicitante is None
    assert detalhe.criador_sistema == "bot_fiscalizacao"


@pytest.mark.parametrize("valor", ["bot desconhecido", {"id": 1}, 1])
def test_criador_sistema_invalido_falha_fechado(valor):
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json=detalhe_valido(criador_sistema=valor),
            )
        ),
    )

    with pytest.raises(XanoContratoInvalido, match="criador_sistema"):
        executar(cliente.obter_chamado("token", 101))


def test_contratos_tecnicos_preservam_visao_atribuicao_e_idempotencia():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        if requisicao.url.path.endswith("/tecnico/chamados"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 101,
                            "titulo": "Falha",
                            "descricao": "Descrição",
                            "status": "Novo",
                            "prioridade": "Alta",
                            "origem": "manual",
                            "criado_em": 1780000000000,
                            "sla_horas_aplicado": 2,
                            "atribuido_em": None,
                            "ativo": {"id": 1, "nome_ativo": "Totem 01"},
                            "categoria": {"id": 2, "nome": "Falha de Rede"},
                            "solicitante": {"id": 8, "nome": "Gerente"},
                            "tecnico": {"id": None, "nome": None},
                        }
                    ],
                },
            )
        return httpx.Response(200, json=detalhe_valido(atribuido_em=1780000001000))

    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(responder),
    )
    fila = executar(cliente.listar_chamados_tecnico("token", "nao_atribuidos"))
    detalhe = executar(cliente.obter_chamado_tecnico("token", 101))
    assumido = executar(cliente.assumir_chamado_tecnico("token", 101))

    assert fila[0].tecnico is None
    assert fila[0].atribuido_em is None
    assert detalhe.atribuido_em == 1780000001000
    assert assumido.atribuido_em == 1780000001000
    assert str(requisicoes[0].url).endswith(
        "/tecnico/chamados?visao=nao_atribuidos"
    )
    assert requisicoes[2].method == "POST"
    assert json.loads(requisicoes[2].read()) == {}


def test_conflito_tecnico_e_classificado_sem_expor_corpo():
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(409, json={"segredo": "não expor"})
        ),
    )

    with pytest.raises(XanoConflito) as capturado:
        executar(cliente.assumir_chamado_tecnico("token", 101))

    assert "não expor" not in str(capturado.value)


@pytest.mark.parametrize(
    ("status", "erro"),
    [
        (401, XanoNaoAutenticado),
        (403, XanoNaoAutorizado),
        (404, XanoNaoEncontrado),
        (422, XanoEntradaInvalida),
        (500, XanoIndisponivel),
        (503, XanoIndisponivel),
    ],
)
def test_erros_http_sao_classificados_sem_expor_corpo(status, erro):
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(status, json={"segredo": "não expor"})
        ),
    )

    with pytest.raises(erro) as capturado:
        executar(cliente.listar_chamados("token"))

    assert "não expor" not in str(capturado.value)


@pytest.mark.parametrize(
    "resposta",
    [
        [],
        {},
        {"items": "não é coleção"},
        {"items": [None]},
        {
            "items": [
                {
                    "id": 1,
                    "nome_ativo": "Totem",
                    "tipo": "Totem",
                    "status_atual": None,
                }
            ]
        },
    ],
)
def test_resposta_incompativel_falha_fechado(resposta):
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=resposta)
        ),
    )

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_ativos("token"))


def test_timeout_e_conexao_sao_indisponibilidade():
    for erro in (httpx.ReadTimeout("timeout"), httpx.ConnectError("conexão")):
        def falhar(requisicao: httpx.Request, erro=erro):
            raise erro

        cliente = XanoServiceDeskCliente(
            BASE_URL,
            transport=httpx.MockTransport(falhar),
        )
        with pytest.raises(XanoIndisponivel):
            executar(cliente.listar_chamados("token"))


def test_base_dedicada_e_obrigatoria_sem_fallback(monkeypatch):
    monkeypatch.delenv("XANO_SERVICE_DESK_BASE_URL", raising=False)
    monkeypatch.setenv("XANO_AUTH_BASE_URL", "https://xano.example/api:mira-auth")
    monkeypatch.setenv("XANO_BASE_URL", "https://xano.example/api:operacional")
    monkeypatch.setenv("XANO_REQUEST_TIMEOUT_SECONDS", "10")

    with pytest.raises(
        XanoContratoInvalido,
        match="XANO_SERVICE_DESK_BASE_URL",
    ):
        criar_cliente_service_desk()

    monkeypatch.setenv("XANO_SERVICE_DESK_BASE_URL", BASE_URL)
    cliente = criar_cliente_service_desk()
    assert cliente._base_url == BASE_URL
