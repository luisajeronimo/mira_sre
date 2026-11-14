"""Contratos operacionais compartilhados sem dependência da Gestão."""

import asyncio

import httpx
import pytest

from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido
from app.states.auth import AuthState


def test_abertura_global_usa_somente_contratos_operacionais():
    requisicoes = []

    def responder(req):
        requisicoes.append(req)
        if req.method == "GET":
            return httpx.Response(200, json={"ativos": [{"id": 7, "nome": "Totem"}], "categorias": [{"id": 2, "nome": "Rede"}]})
        return httpx.Response(201, json={"chamado": {"id": 101}})

    cliente = XanoServiceDeskCliente("https://xano.example/api:service-desk", transport=httpx.MockTransport(responder))
    opcoes = asyncio.run(cliente.opcoes_abertura_global("token-sintetico"))
    chamado = asyncio.run(cliente.abrir_chamado_global(
        "token-sintetico", ativos_referencia_id=7, categorias_servico_id=2,
        prioridade="Alta", titulo="Falha", descricao="Sem comunicação",
    ))
    assert opcoes["ativos"][0]["id"] == 7
    assert chamado["id"] == 101
    assert [r.url.path for r in requisicoes] == ["/api:service-desk/chamados/abertura/filtros", "/api:service-desk/chamados"]
    assert all("administracao" not in r.url.path for r in requisicoes)


@pytest.mark.parametrize("dados", [
    {"ativos": [None], "categorias": []},
    {"ativos": [], "categorias": ["Rede"]},
    {"ativos": [{"id": 7}], "categorias": []},
    {"ativos": [{"id": True, "nome": "Totem"}], "categorias": []},
    {"ativos": [], "categorias": [{"id": 2, "nome": ""}]},
    {"ativos": None, "categorias": []},
])
def test_catalogo_global_rejeita_resposta_incompativel(dados):
    cliente = XanoServiceDeskCliente("https://xano.example/api:service-desk", transport=httpx.MockTransport(lambda req: httpx.Response(200, json=dados)))
    with pytest.raises(XanoContratoInvalido):
        asyncio.run(cliente.opcoes_abertura_global("token-sintetico"))


@pytest.mark.parametrize("role,permitido", [
    ("tecnico", True), ("diretoria", True), ("administrador", True),
    ("gerente", False), ("admin", False), ("", False),
])
def test_grupo_operacional_preserva_identidade(role, permitido):
    estado = AuthState(_reflex_internal_init=True)
    estado.role = role
    assert estado.perfil_operacional is permitido
    assert estado.role == role
