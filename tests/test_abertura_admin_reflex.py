"""Fluxo compartilhado de abertura manual com dados fictícios, sem escrita live."""

from __future__ import annotations

import asyncio
import pytest
from importlib import import_module

from app.chamados.administrador import AberturaAdminState
from app.chamados.gerente.pages import formulario_abertura
from app.states.auth import AuthState

modulo = import_module("app.chamados.administrador")


def coletar(handler, estado, *args):
    async def interno():
        return [evento async for evento in handler.fn(estado, *args)]
    return asyncio.run(interno())


def estado(role="administrador"):
    raiz = AuthState(_reflex_internal_init=True)
    atual = AberturaAdminState(parent_state=raiz, _reflex_internal_init=True)
    raiz._auth_token = "token-ficticio"
    raiz.usuario_id = 12
    raiz.role = role
    raiz.sessao_confirmada = True
    return atual


class ClienteFalso:
    def __init__(self):
        self.aberturas = []
        self.consultas = []

    async def opcoes_abertura_global(self, token):
        self.consultas.append("abertura")
        return {"ativos": [{"id": 17, "nome": "Totem Outra Loja"}], "categorias": [{"id": 2, "nome": "Rede"}]}

    async def abrir_chamado_global(self, token, **dados):
        self.aberturas.append((token, dados))
        return {"id": 91}


async def guard_falso(self, *_args):
    yield None


@pytest.mark.parametrize("role", ["tecnico", "diretoria", "administrador"])
def test_perfis_operacionais_abrem_com_formulario_compartilhado(monkeypatch, role):
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_service_desk", lambda: cliente)
    monkeypatch.setattr(AberturaAdminState, "_executar_guard", guard_falso)
    atual = estado(role)

    coletar(AberturaAdminState.carregar_formulario, atual)
    assert atual.ativos_formulario == [{"id": 17, "nome": "Totem Outra Loja"}]
    assert atual.categorias_formulario == [{"id": 2, "nome": "Rede"}]
    assert formulario_abertura(AberturaAdminState, "qualquer Totem da rede") is not None

    atual.ativo_formulario = "17"
    atual.categoria_formulario = "2"
    atual.prioridade_formulario = "Média"
    atual.titulo_formulario = "Falha de teste"
    atual.descricao_formulario = "Descrição de teste"
    eventos = coletar(AberturaAdminState.abrir_chamado, atual)

    assert cliente.aberturas == [("token-ficticio", {
        "ativos_referencia_id": 17, "categorias_servico_id": 2,
        "prioridade": "Média", "titulo": "Falha de teste", "descricao": "Descrição de teste",
    })]
    assert eventos[-1].args[0][1]._var_value == "/chamados/91"


def test_perfil_indevido_nao_consulta_nem_abre(monkeypatch):
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_service_desk", lambda: cliente)
    monkeypatch.setattr(AberturaAdminState, "_executar_guard", guard_falso)
    atual = estado("gerente")
    coletar(AberturaAdminState.carregar_formulario, atual)
    coletar(AberturaAdminState.abrir_chamado, atual)
    assert cliente.consultas == []
    assert cliente.aberturas == []
